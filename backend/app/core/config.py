import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Configuration
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost", 
        "http://localhost:3000", 
        "http://localhost:8080", 
        "http://localhost:8000", 
        "http://frontend:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "*"
    ]
    
    # Database Configuration
    DATABASE_URL: Optional[PostgresDsn] = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/aiaudio")
    
    # Redis Configuration
    REDIS_URL: Optional[RedisDsn] = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Audio Processing Configuration
    MAX_AUDIO_SIZE_MB: int = 10
    SUPPORTED_AUDIO_FORMATS: List[str] = ["wav", "mp3", "ogg", "m4a", "flac"]
    AUDIO_STORAGE_PATH: str = os.getenv("AUDIO_STORAGE_PATH", "/app/audio_storage")
    
    # Keyword Detection Configuration
    DEFAULT_KEYWORD_THRESHOLD: float = 0.7  # Confidence threshold for keyword detection
    
    model_config = SettingsConfigDict(case_sensitive=True)
    
    @field_validator("OPENAI_API_KEY")
    def validate_openai_api_key(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            print("Warning: OPENAI_API_KEY not set. Some features may not work correctly.")
        return v


settings = Settings()
