import httpx
import jwt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from dotenv import load_dotenv  
import os
from users.dtos.schemas import UserCreate
from users.models.user import User
from sqlalchemy.exc import SQLAlchemyError
from config.config import Session
from users.models.enums import UserType
load_dotenv()
class UsersService:
    """Service class that encapsulates all user-related business logic."""

    def __init__(self):
        # cache env configuration for easy access inside methods
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
        self.ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))
        self.db = Session()

    async def exchange_auth_code_for_token(self, auth_code: str):
        try:
            url = "https://oauth2.googleapis.com/tokeninfo"
            params = {"id_token": auth_code}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                user_info = response.json()

                # Generate your own JWT token
                token_data = {
                    "sub": user_info["sub"],
                    "email": user_info["email"],
                    "name": user_info["name"],
                    "picture": user_info["picture"],
                    "exp": datetime.utcnow() + timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS)
                }
                user = await self.get_user(token_data["email"])
                if user is None:
                    # Create a UserCreate object instead of User
                    user_data = UserCreate(
                        email=token_data["email"], 
                        name=token_data["name"], 
                        profile_url=token_data["picture"], 
                        type=UserType.REGULAR_USER.value, 
                        last_time_service_used=datetime.now(), 
                        blackListed=False, 
                        notes=None
                    )
                    await self.create_user(user_data)
                else:
                    await self.update_last_time_service_used(token_data["email"])
                
                token = jwt.encode(token_data, self.SECRET_KEY, algorithm=self.ALGORITHM)
                print("This is the token", token)
                # Add token to the response JSON
                user_info['token'] = token
                
                # Return the user info with the token
                return {"token": token, "user_info": user_info}
        except Exception as e:
            print("This is the error", e)
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_jwt_token_for_chatbot(self, request: Request):
        user_id = None
        payload = await request.json()
        token = payload.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Missing authentication token")
            
        try:
            # Verify JWT token
            extracted_payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            # Store user info for later use if needed
            user_email = extracted_payload.get("email")
            user = await self.get_user(user_email)
            if user.blackListed:
                return None
            user_id = user.id
            print(f"Token verified for user: {user_email}")
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")
        except Exception:
            raise HTTPException(status_code=400, detail="Token verification failed")
        

    async def verify_jwt_token(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            request.state.user = payload  # Attach user info to request state
            # Fix: Add await keyword to get_user call
            user = await self.get_user(payload["email"])
            
            if user is not None:
                await self.update_last_time_service_used(payload["email"])
            else:
                return
                
            return payload  # Return payload for direct use in routes
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def create_user(self, user: UserCreate):
        try:
            # Check if we're receiving a UserCreate (which has .dict()) or a User instance
            if hasattr(user, 'dict'):
                db_user = User(**user.dict())
            else:
                # If user is already a User instance, use it directly
                db_user = user
                
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()

    async def blacklist_user(self, user_email: str):
        try:
            db_user = self.db.query(User).filter(User.email == user_email).first()
            if db_user:
                db_user.blackListed = True
                self.db.commit()
                self.db.refresh(db_user)
                return db_user
            else:
                print(f"User not found for email: {user_email}")
                return None
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"SQL error in blacklist_user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.db.rollback()
            print(f"Unexpected error in blacklist_user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()


    async def get_user(self, user_email: str):
        try:
            db_user = self.db.query(User).filter(User.email == user_email).first()
            return db_user
        except SQLAlchemyError as e:
            print(f"SQL error in get_user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            print(f"Unexpected error in get_user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()

    async def update_last_time_service_used(self, user_email: str):
        try:
            db_user = self.db.query(User).filter(User.email == user_email).first()
            if db_user:
                db_user.last_time_service_used = datetime.now()
                self.db.commit()
                self.db.refresh(db_user)
                return db_user
            else:
                print(f"User not found for email: {user_email}")
                return None
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"SQL error in update_last_time_service_used: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.db.rollback()
            print(f"Unexpected error in update_last_time_service_used: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()