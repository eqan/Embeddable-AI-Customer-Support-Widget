from fastapi import APIRouter, Request
from chatbot.dtos.chatbot import ChatbotRequest
from chatbot.chatbotService import generate_result
from config.config import limiter
import jwt
from config.settings import Settings
from users.usersService import get_user

settings = Settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

router = APIRouter()


@router.post("/chatbot-response")
@limiter.limit("5/second")
async def chatbot_response(request: Request):
    try:
        payload = await request.json()
        token = payload.get("token")
        if not token:
            return {"code": 400, "error": "Missing authentication token"}
            
        try:
            # Verify JWT token
            extracted_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # Store user info for later use if needed
            user_email = extracted_payload.get("email")
            user = await get_user(user_email)
            if user.blackListed:
                return {"code": 400, "error": "User is blacklisted"}
            print(f"Token verified for user: {user_email}")
        except jwt.ExpiredSignatureError:
            return {"code": 400, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"code": 400, "error": "Invalid token"}
        except Exception as e:
            return {"code": 400, "error": "Token verification failed"}
            
        # Only accept connection if token is valid
        chatbot_request = None
        try:
        	payload = await request.json()
        	chatbot_request = ChatbotRequest(**payload)
        except Exception as e:
        	return {"code": 400, "error": "Invalid payload"}
        if chatbot_request is not None:
        	return await generate_result(chatbot_request)
        else:
        	return {"code": 400, "error": "Invalid payload"}
    except Exception as e:
        return {"code": 400, "error": "Invalid payload"}