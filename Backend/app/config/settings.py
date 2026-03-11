from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    logging_level: str = "WARNING"
    model_api_key: str = ""
    model_name: str = "gemini-2.5-flash"
    model_api_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    allowed_origins: str = "*"
    db_user: str
    db_password: str = ""
    db_host: str = "127.0.0.1"
    db_name: str
    google_oauth_url: str = "https://oauth2.googleapis.com/tokeninfo"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_days: int = 7
    sentry_dsn: str = ""
    firecrawl_api_key: str = Field(default="", validation_alias="FIRECRAWL")
    voyage_api_key: str = ""
    embedding_model: str = "voyage-3"
    reasoning_model_api_key: str = ""
    pinecone_index_name: str = ""
    pinecone_api_key: str = ""
    pinecone_host: str = ""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        extra="allow",
    )

settings = Settings()