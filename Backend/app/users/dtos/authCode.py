from pydantic import BaseModel

class AuthCodePayload(BaseModel):
    code: str
