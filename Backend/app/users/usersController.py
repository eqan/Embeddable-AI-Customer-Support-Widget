from fastapi import APIRouter, HTTPException, Depends
import httpx
from users.dtos.authCode import AuthCodePayload
from users.usersService import exchange_auth_code_for_token, verify_jwt_token

router = APIRouter()

@router.post("/google-login")
async def google_login(payload: AuthCodePayload):
    try:
        user_info = await exchange_auth_code_for_token(payload.code)
        return {"status": True, "message": "Google Authentication Successful!", "result": user_info}
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="Google authentication failed")

@router.get("/verify-token")
async def verify_token_route(user_payload: dict = Depends(verify_jwt_token)):
    # If the token is valid, this route will return the user payload
    return {"status": True, "user": user_payload}

