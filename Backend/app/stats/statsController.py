from fastapi import APIRouter
from stats.statsService import stats_service
from fastapi import Request, HTTPException
from users.usersService import users_service
from config.config import limiter

router = APIRouter()
@router.post("/stats", tags=["Stats"])
@limiter.limit("5/second")
async def generate_stats_endpoint(request: Request):
    """
    This endpoint generates stats for a user.\n
    Body Parameters:
    - token: str
        The token for authentication.
    """
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return await stats_service.generate_stats(user_id)

@router.get("/stats", tags=["Stats"])
@limiter.limit("5/second")
async def get_stats_endpoint(request: Request):
    """
    This endpoint gets stats for a user.\n
    Body Parameters:
    - token: str
        The token for authentication.
    """
    user_id = await users_service.verify_jwt_token_for_chatbot(request)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User is blacklisted")
    return await stats_service.get_stats(user_id)