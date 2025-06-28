import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    API_KEY: str = os.getenv("API_KEY")
    REDIS_URL: str = "redis://localhost:6379"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_MIME_TYPES = {
        "text/plain": "txt",
        "application/pdf": "pdf"
    }

settings = Settings()