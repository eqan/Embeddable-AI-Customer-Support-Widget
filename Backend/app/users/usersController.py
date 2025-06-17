from fastapi import APIRouter, HTTPException, Depends
import httpx
from users.dtos.authCode import AuthCodePayload
from users.usersService import users_service

router = APIRouter()

@router.post("/google-login", tags=["Users"])
async def google_login(payload: AuthCodePayload):
    """
    This endpoint exchanges a Google authentication code for a token and user information.\n
    Body Parameters:
    - code: str
        The Google authentication code.
    """
    try:
        user_info = await users_service.exchange_auth_code_for_token(payload.code)
        return {"status": True, "message": "Google Authentication Successful!", "result": user_info}
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="Google authentication failed")

@router.get("/verify-token", tags=["Users"])
async def verify_token_route(user_payload: dict = Depends(users_service.verify_jwt_token)):
    """
    This endpoint verifies a JWT token and returns the user payload.\n
    Body Parameters:
    - token: str
        The JWT token to verify.
    """
    # If the token is valid, this route will return the user payload
    return {"status": True, "user": user_payload}