import os
from dotenv import load_dotenv

# CRITICAL: Load environment variables FIRST before any other imports
load_dotenv()

# Now import FastAPI and other dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import chat module after dotenv is loaded
from app.api import chat

# 1. Security & Config
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="BoardMax API")

# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Register Routes
app.include_router(chat.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "online", "system": "BoardMax Intelligence Ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)