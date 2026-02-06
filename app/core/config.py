from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str
    app_env: str
    app_host: str
    app_port: int

    # Database
    database_url: str

    # Redis
    redis_url: str | None = None

    # OpenAI
    openai_api_key: str

    # GitHub
    github_token: str | None = None

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Logging
    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
