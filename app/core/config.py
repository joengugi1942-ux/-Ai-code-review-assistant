"""
Application configuration using Pydantic settings.

Loads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str
    app_env: str
    app_host: str
    app_port: int

    # Database
    database_url: str

    # Redis
    redis_url: str | None = None

    # Groq
    groq_api_key: str

    # GitHub
    github_token: str | None = None

    # API Authentication
    api_key: str

    # Admin API Key (for generating/managing API keys)
    admin_api_key: str | None = None

    # JWT (optional - not used currently)
    secret_key: str | None = None
    algorithm: str | None = None
    access_token_expire_minutes: int | None = None

    # Logging
    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
