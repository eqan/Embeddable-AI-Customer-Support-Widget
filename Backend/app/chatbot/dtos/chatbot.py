from pydantic import BaseModel, constr

class ChatbotRequest(BaseModel):
    message: constr(max_length=10000)
    token: constr(max_length=500)
    session_id: constr(max_length=300)
    chat_history: list[dict]
    website_url: constr(max_length=2083)  # Common max length for URLs
    website_description: constr(max_length=10000)