from fastapi import APIRouter
from stats.statsService import StatsService
from fastapi import Request, HTTPException
from users.usersService import UsersService
from config.config import limiter

router = APIRouter()

# Global UsersService instance
users_service = UsersService()

# Global StatsService instance
stats_service = StatsService()

@router.post("/stats")
@limiter.limit("5/second")
async def generate_stats_endpoint(request: Request):
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return await stats_service.generate_stats(user_id)

@router.get("/stats")
@limiter.limit("5/second")
async def get_stats_endpoint(request: Request):
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return await stats_service.get_stats(user_id)