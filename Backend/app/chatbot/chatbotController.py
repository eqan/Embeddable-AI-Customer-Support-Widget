from fastapi import APIRouter, Request
from chatbot.dtos.chatbot import ChatbotRequest
from chatbot.chatbotService import generate_result
from config.config import limiter

router = APIRouter()


@router.post("/chatbot-response")
@limiter.limit("5/second")
async def chatbot_response(request: Request):
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