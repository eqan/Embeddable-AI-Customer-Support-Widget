from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot.chatbotController import router as chatbot_router
from users.usersController import router as user_router
from stats.statsController import router as stats_router
from config.config import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from config.settings import Settings
from database import create_tables
from stats.scheduler import scheduler
import uvicorn

settings = Settings()

app = FastAPI()

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
app.include_router(user_router)
app.include_router(stats_router)

@app.get("/")
async def root():
    return {"message": "Embedded Chatbot API is running!"}

# ---------------------------------------------------------------------------
# Scheduler lifecycle hooks
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def _start_scheduler():
    scheduler.start()


@app.on_event("shutdown")
async def _shutdown_scheduler():
    scheduler.shutdown()

if __name__ == "__main__":
   create_tables()
   uvicorn.run(app, host="0.0.0.0", port=8000)
