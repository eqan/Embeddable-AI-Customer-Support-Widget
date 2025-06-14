from fastapi import APIRouter
from stats.statsService import generate_stats
from fastapi import Request, HTTPException
from users.usersService import verify_jwt_token_for_chatbot
from config.config import limiter

router = APIRouter()

@router.get("/stats")
@limiter.limit("5/second")
async def get_stats(request: Request):
    user_id = await verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return await generate_stats(user_id)