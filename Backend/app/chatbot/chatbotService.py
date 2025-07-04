from prompts.load_prompt import load_prompt
from chatbot.dtos.chatbot import ChatbotRequest
from config.config import generation_config, Session
from config.settings import Settings
import requests
import json
from chatbot.dtos.chatbot_response import ChatbotResponse
from ticket.ticketService import TicketService
from pydantic import ValidationError as ResponseValidationError
from fastapi import HTTPException
import re
from chatbot.models.chat import Chat
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid
from ticket.dtos.ticket import TicketCreate
from ingestion.dtos.ingestion import SearchDTO
from ingestion.ingestionService import ingestion_service

# Singleton-like settings instance (can be shared across class instances)
settings = Settings()

class ChatbotService:
    """Service encapsulating all chatbot-related logic including LLM calls and DB ops."""
    def __init__(self):
        self.MAX_ATTEMPTS = 5
        self.db = Session()
        self.ticket_service = TicketService()

    @staticmethod
    def _extract_json_from_parts(parts: list[dict]) -> str:
        """Return the first JSON object found inside the candidate parts array.

        Gemini sometimes returns plain-text followed by a Markdown code-block that
        contains the structured JSON we asked for.  This helper walks the parts in
        reverse order (most specific content last) and extracts the substring
        between the first opening and its matching closing curly brace.
        """
        for part in reversed(parts):
            if not isinstance(part, dict):
                continue
            txt = part.get("text", "")
            # Quickly skip if there is no opening brace
            if "{" not in txt:
                continue
            # Remove ```json fenced code block markers if present
            cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", txt).strip()
            # Grab the JSON substring (from first '{' to last '}')
            m_start = cleaned.find("{")
            m_end = cleaned.rfind("}")
            if m_start != -1 and m_end != -1 and m_end > m_start:
                possible_json = cleaned[m_start : m_end + 1]
                try:
                    # validate quickly
                    json.loads(possible_json)
                    return possible_json
                except json.JSONDecodeError:
                    continue
        raise ValueError("No JSON object found in LLM response parts")

    @staticmethod
    def _clean_and_parse_json(response_text: str) -> ChatbotResponse:
        """Clean Gemini's response text and parse it as ChatbotResponse model."""
        # Remove markdown code blocks
        cleaned_text = re.sub(r'```(?:json)?\s*|\s*```', '', response_text)

        # Remove escaped quotes
        cleaned_text = cleaned_text.replace('\\"', '"')

        # Strip whitespace
        cleaned_text = cleaned_text.strip()

        # Parse JSON
        parsed_json = json.loads(cleaned_text)

        # Validate JSON against expected schema using pydantic model
        try:
            validated = ChatbotResponse(**parsed_json)
        except ResponseValidationError as e:
            # Re-raise as JSONDecodeError to keep existing error handling semantics
            raise json.JSONDecodeError(f"LLM response schema mismatch: {e}", cleaned_text, 0)

        return validated

    # -------------------------
    # Public Async Methods
    # -------------------------

    async def generate_result(self, chatbot_request: ChatbotRequest, user_id: int) -> ChatbotResponse:
        """Call Gemini LLM with retries and return validated response."""
        model_name = settings.model_name or "gemini-2.0-flash"
        
        relevant_content = ""
        try:
            data = ingestion_service.search_in_pinecone(SearchDTO(query=chatbot_request.message, company_website=chatbot_request.website_url, top_k=4))
            i = 0
            for match in data["matches"]:
                try:
                    relevant_content += f"Entry {i}: Title: {match["metadata"]["title"]} Content Type: {match["metadata"]["content_type"]} Section: {match["metadata"]["section"]} Source URL: {match["metadata"]["source_url"]} Content: {match["metadata"]["cleaned_content"]} Metadata: {match["metadata"]["specific_metadata"]}\n\n"
                    i += 1
                except Exception as e:
                    print(f"Error getting transcript: {e}")
        except Exception as e:
            print("Error coming in:", e)

        prompt = load_prompt("response-generation")
        prompt = prompt.replace("{website_url}", chatbot_request.website_url)
        prompt = prompt.replace("{message}", chatbot_request.message)
        prompt = prompt.replace("{website_description}", chatbot_request.website_description)
        prompt = prompt.replace("{relevant_content}", relevant_content)
        print("relevant_content", relevant_content)

        # Build the request payload with Google Search grounding
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.model_api_key}"

        # chat_history is assumed to be a list like:
        # [{"role": "user", "content": "Hi"},
        #  {"role": "model","content": "Hello!"}]
        history_contents = [
            {"role": turn["role"], "parts": [{"text": turn["content"]}]}
            for turn in chatbot_request.chat_history
        ]

        payload = {
            "contents": [
                {"role": "model", "parts": [{"text": prompt}]}
            ] + history_contents + [
                {"role": "user", "parts": [{"text": chatbot_request.message}]}
            ],
            "generationConfig": generation_config,
              "tools": [
                { "googleSearch": {} },
            ]
        }

        headers = {"Content-Type": "application/json"}

        last_error: Exception | None = None

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                resp = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=60)
                data = resp.json()

                if not resp.ok:
                    raise HTTPException(status_code=resp.status_code, detail=f"Upstream LLM error: {resp.text}")

                try:
                    parts = data["candidates"][0]["content"]["parts"]
                except (KeyError, IndexError):
                    raise HTTPException(status_code=500, detail="Unexpected response structure from LLM")

                json_block = self._extract_json_from_parts(parts)

                # Will raise JSONDecodeError on schema mismatch which we catch below.
                response = self._clean_and_parse_json(json_block)
                chatbot_request.chat_history.append({"role": "model", "content": response.response, "is_booking": response.is_booking, "is_human_handoff": response.is_human_handoff})
                await self.save_chat_history(chatbot_request, user_id)
                if response.is_human_handoff:
                    try:
                        ticket_uuid = "TICKET-" + str(uuid.uuid4())
                        self.ticket_service.create_ticket(TicketCreate(
                            user_id=user_id,
                            message=chatbot_request.message,
                            session_id=chatbot_request.session_id,
                            uuid=ticket_uuid
                        ))
                        response.ticket_uuid = ticket_uuid
                    except Exception as e:
                        print(f"Error creating ticket: {e}")
                return response

            except (HTTPException, ValueError, json.JSONDecodeError) as err:
                last_error = err
                # On the final attempt re-raise, otherwise try again.
                if attempt == self.MAX_ATTEMPTS:
                    raise last_error
                print(f"Retrying Gemini call after error: {err}")

        raise last_error if last_error else HTTPException(status_code=500, detail="Failed to get valid response from LLM")

    async def save_chat_history(self, chatbot_request: ChatbotRequest, user_id: int):
        try:
            existing_history = await self.get_chat_history(chatbot_request.session_id)
            if existing_history:
                # Update and return the updated chat history entry
                return await self.update_chat_history(chatbot_request)

            # No previous history ‑ create a new record
            chat = Chat(
                user_id=user_id,
                session_id=chatbot_request.session_id,
                message=chatbot_request.message,
                chat_history=str(chatbot_request.chat_history),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(chat)
            self.db.commit()
            self.db.refresh(chat)
            return chat
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()

    async def get_chat_history(self, session_id: str):
        try:
            # Get chat history for the given session_id
            chat_history = self.db.query(Chat).filter(Chat.session_id == session_id).all()
            if chat_history:
                return chat_history
            else:
                return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()

    async def get_all_chats(self, user_id: int):
        try:
            chats = self.db.query(Chat).filter(Chat.user_id == user_id).all()
            return chats
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()

    async def update_chat_history(self, chatbot_request: ChatbotRequest):
        try:
            chat = self.db.query(Chat).filter(Chat.session_id == chatbot_request.session_id).first()
            if chat:
                chat.message = chatbot_request.message
                chat.chat_history = str(chatbot_request.chat_history)
                chat.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(chat)
            return chat
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()

chatbot_service = ChatbotService()