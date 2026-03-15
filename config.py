import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///gifts.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    APP_URL = os.getenv("APP_URL", "https://your-app.railway.app")  # URL мини-аппа
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
