from fastapi import APIRouter, Request, HTTPException, Depends
from chatbot.dtos.chatbot import ChatbotRequest
from chatbot.dtos.chatbot_response import ChatbotResponse
from chatbot.chatbotService import generate_result
from config.config import limiter
from users.usersService import verify_jwt_token_for_chatbot
from utils.security import enforce_payload_size
from chatbot.chatbotService import get_all_chats

router = APIRouter()


@router.post("/chatbot-response", response_model=ChatbotResponse, dependencies=[Depends(enforce_payload_size)])
@limiter.limit("5/second")
async def chatbot_response(request: Request):
    try:
        user_id = await verify_jwt_token_for_chatbot(request)
        if user_id is None:
        	raise HTTPException(status_code=400, detail="User is blacklisted")
        # Only accept connection if token is valid
        chatbot_request = None
        try:
        	payload = await request.json()
        	chatbot_request = ChatbotRequest(**payload)
        except Exception:
        	raise HTTPException(status_code=400, detail="Invalid payload")
        if chatbot_request is not None:
        	return await generate_result(chatbot_request, user_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")
    
@router.get("/all-chats")
async def get_all_chats_endpoint(request: Request):
    user_id = await verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return await get_all_chats(user_id)