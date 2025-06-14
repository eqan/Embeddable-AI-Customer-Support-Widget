from ticket.ticketService import TicketService
from ticket.dtos.ticket import TicketUpdate
from fastapi import APIRouter, Request, HTTPException
from config.config import limiter
from users.usersService import UsersService
from utils.security import enforce_payload_size
from fastapi import Depends

router = APIRouter()
ticket_service = TicketService()

# Global instance of UsersService
users_service = UsersService()

@router.put("/ticket", dependencies=[Depends(enforce_payload_size)])
@limiter.limit("5/second")
async def update_ticket(
    request: Request,
):
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    payload = await request.json()
    ticket = TicketUpdate(**payload)
    return ticket_service.update_ticket(ticket)

@router.get("/ticket/{uuid}")
@limiter.limit("5/second")
async def get_ticket(
    request: Request,
):
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    payload = await request.json()
    uuid = payload.get("uuid")
    if uuid is None:
        raise HTTPException(status_code=400, detail="UUID is required")
    return ticket_service.get_ticket(uuid)

@router.get("/tickets")
@limiter.limit("5/second")
async def get_all_tickets_by_user_id(
    request: Request,
):
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return ticket_service.get_all_tickets_by_user_id(user_id)