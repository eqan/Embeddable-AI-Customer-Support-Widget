from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
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
    """Non-streaming chatbot endpoint (backward-compatible). Returns a single JSON response."""
    try:
        user_id = await users_service.verify_jwt_token_for_chatbot(request)
        if user_id is None:
            raise HTTPException(status_code=400, detail="User is blacklisted")
        return await chatbot_service.generate_result(chatbot_request, user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chatbot-response/stream", dependencies=[Depends(enforce_payload_size)], tags=["Chatbot"])
@limiter.limit("5/second")
async def chatbot_response_stream(chatbot_request: ChatbotRequest, request: Request):
    """SSE streaming chatbot endpoint using a two-phase architecture.

    Phase 1 (Intent Classification):
        A lightweight Gemini call classifies the user's intent as
        "regular", "booking", or "handoff" (~200-500ms).

    Phase 2 (Conditional Response):
        - regular  -> streams text tokens via Gemini streamGenerateContent
        - booking  -> single action event with acknowledgment text
        - handoff  -> creates ticket, single action event with ticket UUID

    SSE Event Protocol:
        event: intent  -> {"type": "regular"|"booking"|"handoff"}
        event: token   -> {"text": "chunk"}
        event: action  -> {"type":..., "response":..., "ticket_uuid":...}
        event: done    -> {"is_booking": bool, "is_human_handoff": bool}
        event: error   -> {"message": str, "code": int}
    """
    try:
        user_id = await users_service.verify_jwt_token_for_chatbot(request)
        if user_id is None:
            raise HTTPException(status_code=400, detail="User is blacklisted")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StreamingResponse(
        chatbot_service.stream_response_sse(chatbot_request, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
    
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