from pydantic import BaseModel
from typing import Optional

class ChatbotRequest(BaseModel):
    message: str
    user_email: str
    session_id: str
    chat_history: Optional[list[dict]] = None
    website_url: Optional[str] = None