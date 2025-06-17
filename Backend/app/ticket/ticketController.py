from ticket.ticketService import ticket_service
from ticket.dtos.ticket import TicketUpdate
from fastapi import APIRouter, Request, HTTPException
from config.config import limiter
from users.usersService import users_service
from utils.security import enforce_payload_size
from fastapi import Depends

router = APIRouter()
@router.put("/ticket", dependencies=[Depends(enforce_payload_size)], tags=["Ticket"])
@limiter.limit("5/second")
async def update_ticket(
    ticket: TicketUpdate,
    request: Request,
):
    """
    This endpoint updates a ticket.\n
    Body Parameters:
    - uuid: str
        The UUID of the ticket to update.
    - status: str
        The status of the ticket to update.
    """
    return ticket_service.update_ticket(ticket)

@router.get("/ticket/{uuid}", tags=["Ticket"])
@limiter.limit("5/second")
async def get_ticket(
    uuid: str,
    request: Request,
):
    """
    This endpoint gets a ticket by UUID.\n
    Body Parameters:
    - uuid: str
        The UUID of the ticket to get.
    """
    return ticket_service.get_ticket(uuid)

@router.get("/tickets", tags=["Ticket"])
@limiter.limit("5/second")
async def get_all_tickets_by_user_id(
    request: Request,
):
    """
    This endpoint gets all tickets for a user.\n
    Body Parameters:
    - token: str
        The token for authentication.
    """
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return ticket_service.get_all_tickets_by_user_id(user_id)