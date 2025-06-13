from slowapi import Limiter
from slowapi.util import get_remote_address
import google.generativeai as genai
from config.settings import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = Settings()

# Create a limiter instance with the default rate
limiter = Limiter(key_func=get_remote_address)

#@title Model Configuration
# Model settings for generating responses
generation_config = {
  "temperature": 1,   # Creativity (0: deterministic, 1: high variety)
  "top_p": 0.95,       # Focus on high-probability words
  "top_k": 64,        # Consider top-k words for each step
  "max_output_tokens": 8192,  # Limit response length
  "response_mime_type": "text/plain",  # Output as plain text
}

safety_settings = [
  # Gemini's safety settings for blocking harmful content
  # (Set to "BLOCK_ALL" for blocking)
  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ALL"},
  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ALL"},
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ALL"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ALL"},
]

genai.configure(api_key=settings.model_api_key)

# Suppose you have an array with credentials in the order: [USER, PASSWORD, HOST, PORT, DATABASE]
credentials = {
    "DB_USER": settings.db_user,
    "DB_PASSWORD": settings.db_password,
    "DB_HOST": settings.db_host,
    "DB_NAME": settings.db_name,
}
# Unpack the array into the database URL
database_url = f"postgresql://{credentials['DB_USER']}:{credentials['DB_PASSWORD']}@{credentials['DB_HOST']}/{credentials['DB_NAME']}"

# Create an engine
engine = create_engine(
    database_url,
    pool_size=10,  # Maximum number of connections to keep
    max_overflow=20,  # Maximum number of connections to allow beyond the pool size
    pool_timeout=30,  # Seconds to wait before timing out on getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes (prevent stale connections)
    pool_pre_ping=True,  # Verify connection is active before using it
    connect_args={
        "sslmode": "require",  # Require SSL connection
        "connect_timeout": 10,  # Connection timeout in seconds
        "keepalives": 1,  # Enable keepalives
        "keepalives_idle": 60,  # Seconds between keepalives
        "keepalives_interval": 10,  # Seconds between keepalive probes
        "keepalives_count": 5,  # Number of keepalive probes before considering connection dead
    },
)

# Create a session
Session = sessionmaker(bind=engine)