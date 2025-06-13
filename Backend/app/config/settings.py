import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    logging_level: str = "WARNING"
    model_api_key: str = os.getenv("MODEL_API_KEY")
    model_name: str = os.getenv("MODEL_NAME")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS")
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        extra="allow",
    )
