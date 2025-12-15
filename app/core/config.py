from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Code Review Assistant"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    openai_api_key: str | None = None
    github_token: str | None = None

    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


