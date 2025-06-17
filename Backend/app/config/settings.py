import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    logging_level: str = "WARNING"
    model_api_key: str = os.getenv("MODEL_API_KEY")
    model_name: str = os.getenv("MODEL_NAME")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")
    db_host: str = os.getenv("DB_HOST")
    db_name: str = os.getenv("DB_NAME")
    google_oauth_url: str = os.getenv("GOOGLE_OAUTH_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_days: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))
    sentry_dsn: str = os.getenv("SENTRY_DSN")
    astra_db_client_secret: str = os.getenv("ASTRA_CS")
    astra_db_api_endpoint: str = os.getenv("ASTRA_DB_ENDPOINT")
    firecrawl_api_key: str = os.getenv("FIRECRAWL")
    voyage_api_key: str = os.getenv("VOYAGE_API_KEY")
    embedding_model: str = os.getenv("EMBEDDING_MODEL")
    reasoning_model_api_key: str = os.getenv("REASONING_MODEL_API_KEY")
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        extra="allow",
    )

settings = Settings()