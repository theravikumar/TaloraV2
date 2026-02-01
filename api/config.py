# api/config.py
"""
Configuration management for Talora API
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """API Settings loaded from environment"""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    # Database
    database_url: str
    redis_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # File Upload
    max_upload_size_mb: int = 5
    upload_dir: str = "data/uploads"
    
    # Session
    session_timeout_minutes: int = 5
    
    # ClamAV
    clamav_host: str = "localhost"
    clamav_port: int = 3310
    
    # LLM (from existing config)
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra env variables from existing .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
