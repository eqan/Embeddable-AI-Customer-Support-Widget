from fastapi import APIRouter, Request, HTTPException, Depends
from chatbot.dtos.chatbot import ChatbotRequest
from chatbot.dtos.chatbot_response import ChatbotResponse
from config.config import limiter
from users.usersService import users_service
from chatbot.chatbotService import chatbot_service
from utils.security import enforce_payload_size

router = APIRouter()

@router.post("/chatbot-response", response_model=ChatbotResponse, dependencies=[Depends(enforce_payload_size)], tags=["Chatbot"])
@limiter.limit("5/second")
async def chatbot_response(chatbot_request: ChatbotRequest, request: Request):
    """
    This endpoint processes a chatbot request and returns a structured response.

    Body Parameters:
    - chatbot_request: ChatbotRequest
        The request body should contain the following fields:
        - message: str
            The message from the user to the chatbot.
        - token: str
            The token for authentication.
        - session_id: str
            The session identifier for the conversation.
        - chat_history: list[dict]
            The history of the chat conversation.
        - website_url: str
            The URL of the website.
        - website_description: str
            The description of the website.
    """
    try:
        user_id = await users_service.verify_jwt_token_for_chatbot(request)
        if user_id is None:
        	raise HTTPException(status_code=400, detail="User is blacklisted")
        # Only accept connection if token is valid and request body was successfully parsed
        return await chatbot_service.generate_result(chatbot_request, user_id)
    except HTTPException as e:      # propagate real HTTP errors
        raise e
    except Exception as e:          # everything else → 500 or your choice
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all-chats", tags=["Chatbot"])
async def get_all_chats_endpoint(request: Request):
    """
    This endpoint returns all chats for a user.\n
    Body Parameters:
    - token: str
        The token for authentication.
    """
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return await chatbot_service.get_all_chats(user_id)