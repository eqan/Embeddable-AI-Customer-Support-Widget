from pydantic import BaseModel

class ChatbotRequest(BaseModel):
    message: str
    token: str
    session_id: str
    chat_history: list[dict] = None
    website_url: str = None
    website_description: str = None