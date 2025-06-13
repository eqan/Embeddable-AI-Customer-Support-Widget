from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot.chatbotController import router as chatbot_router
from config.config import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from config.settings import Settings

settings = Settings()

app = FastAPI()

def parse_urls():
    origins = settings.allowed_origins
    if "," in origins:
        return [url.strip() for url in origins.split(",")]
    return [origins.strip()]

# Add the rate limiter middleware to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["POST", "GET"],  # Allows only POST method
    allow_headers=["*"],  # Allows all headers
)


app.include_router(chatbot_router)

@app.get("/")
async def root():
    return {"message": "Embedded Chatbot API is running!"}
