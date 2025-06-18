from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "StackSense"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://rayyanalikhan@localhost:5432/stacksense"
    )
    SQL_ECHO: bool = False
    
    # Redis settings for caching
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
    REDIS_TTL: int = 3600  # Cache TTL in seconds
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECTS_PER_PAGE: int = 10
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    # External API Keys
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    STACKOVERFLOW_API_KEY: Optional[str] = os.getenv("STACKOVERFLOW_API_KEY")
    STACKSHARE_API_KEY: Optional[str] = os.getenv("STACKSHARE_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment variables

# Create settings instance
settings = Settings() 