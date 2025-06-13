from pydantic import BaseModel

class ChatbotRequest(BaseModel):
    message: str
    token: str
    session_id: str
    chat_history: list[dict]
    website_url: str
    website_description: str