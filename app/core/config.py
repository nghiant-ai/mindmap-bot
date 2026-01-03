"""Configuration settings for Mindmap Bot"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # App info
    app_name: str = "Mindmap Bot"
    app_env: str = "development"
    log_level: str = "INFO"

    # Telegram
    telegram_bot_token: str

    # Gemini AI
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
