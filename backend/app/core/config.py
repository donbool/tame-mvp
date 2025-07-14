from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://tame:tame@localhost:5432/tame"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Integrations
    SLACK_WEBHOOK_URL: Optional[str] = None
    GITHUB_WEBHOOK_URL: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security
    JWT_SECRET: str = "your-jwt-secret-change-this"
    HMAC_SECRET: str = "your-hmac-secret-for-log-signing"
    
    # Policy Configuration
    POLICY_FILE: str = "policies.yml"
    POLICY_VERSION_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 