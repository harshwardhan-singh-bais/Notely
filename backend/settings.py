from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal
import os

router = APIRouter()

class UserSettings(BaseModel):
    user_id: str
    gemini_api_key: str = ""
    whisper_api_key: str = ""
    notion_api_key: str = ""
    screenshot_interval: int = 5
    embedding_type: str = "clip"
    llm_preference: str = "gemini"

# Dummy in-memory store for demo (replace with DB logic for production)
USER_SETTINGS = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/settings/{user_id}", response_model=UserSettings)
def get_settings(user_id: str):
    settings = USER_SETTINGS.get(user_id)
    if not settings:
        # Return default settings if not set
        return UserSettings(user_id=user_id)
    return settings

@router.post("/settings/{user_id}", response_model=UserSettings)
def save_settings(user_id: str, settings: UserSettings):
    USER_SETTINGS[user_id] = settings
    return settings
