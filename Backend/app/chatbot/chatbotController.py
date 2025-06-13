from fastapi import APIRouter, Request, HTTPException
from chatbot.dtos.chatbot import ChatbotRequest
from chatbot.dtos.chatbot_response import ChatbotResponse
from chatbot.chatbotService import generate_result
from config.config import limiter
import jwt
from config.settings import Settings
from users.usersService import get_user

settings = Settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

router = APIRouter()


@router.post("/chatbot-response", response_model=ChatbotResponse)
@limiter.limit("5/second")
async def chatbot_response(request: Request):
    try:
        user_id = None
        payload = await request.json()
        token = payload.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Missing authentication token")
            
        try:
            # Verify JWT token
            extracted_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # Store user info for later use if needed
            user_email = extracted_payload.get("email")
            user = await get_user(user_email)
            if user.blackListed:
                return {"code": 400, "error": "User is blacklisted"}
            user_id = user.id
            print(f"Token verified for user: {user_email}")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")
        except Exception:
            raise HTTPException(status_code=400, detail="Token verification failed")
            
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