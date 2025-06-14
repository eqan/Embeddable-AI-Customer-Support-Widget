from pydantic import BaseModel

class TicketCreate(BaseModel):
    message: str
    session_id: str
    user_id: int
    uuid: str

class TicketUpdate(BaseModel):
    uuid: str
    status: str

class DeleteTicket(BaseModel):
    uuid: str