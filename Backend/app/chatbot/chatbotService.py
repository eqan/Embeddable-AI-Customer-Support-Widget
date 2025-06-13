from chatbot.prompts.load_prompt import load_prompt
from chatbot.dtos.chatbot import ChatbotRequest
from config.config import generation_config
from config.settings import Settings
import requests
import json

settings = Settings()

def clean_and_parse_json(response_text):
    """
    Clean Gemini's response text and parse it as JSON.
    
    Args:
        response_text: The raw text response from Gemini
        
    Returns:
        dict: Parsed JSON as Python dictionary
        
    Raises:
        json.JSONDecodeError: If JSON parsing fails
    """
    import json
    import re
    
    # Remove markdown code blocks
    cleaned_text = re.sub(r'```(?:json)?\s*|\s*```', '', response_text)
    
    # Remove escaped quotes
    cleaned_text = cleaned_text.replace('\"', '"')
    
    # Strip whitespace
    cleaned_text = cleaned_text.strip()
    
    # Parse JSON
    return json.loads(cleaned_text)

async def generate_result(chatbot_request: ChatbotRequest):
    model_name = settings.model_name or "gemini-2.0-flash"

    prompt = load_prompt()
    prompt = prompt.replace("{website_url}", chatbot_request.website_url)
    prompt = prompt.replace("{message}", chatbot_request.message)

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
        "contents": history_contents + [
            {"role": "user", "parts": [{"text": chatbot_request.message}]}
        ],
        "generation_config": generation_config,
        "tools": [
            {
                "google_search_retrieval": {
                    "dynamic_retrieval_config": {
                        "mode": "MODE_DYNAMIC",
                        "dynamic_threshold": 0.6
                    }
                }
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    resp = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=60)

    if not resp.ok:
        return {"code": resp.status_code, "error": resp.text}

    data = resp.json()

    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return {"code": 500, "error": "Unexpected response structure", "raw": data}

    return clean_and_parse_json(raw_text)