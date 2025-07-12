import os
from typing import Optional
from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # Database connection settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/microservices_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "microservices_db"
    DATABASE_USER: str = "user"
    DATABASE_PASSWORD: str = "password"
    
    # Connection pool settings
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 30
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600
    
    # Redis settings (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global database settings instance
db_settings = DatabaseSettings()


def get_database_url() -> str:
    """Get the database URL from environment or use default."""
    return os.getenv("DATABASE_URL", db_settings.DATABASE_URL)


def get_redis_url() -> str:
    """Get the Redis URL from environment or use default."""
    return os.getenv("REDIS_URL", db_settings.REDIS_URL)