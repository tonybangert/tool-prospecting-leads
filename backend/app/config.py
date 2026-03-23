"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/prospect_brief"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    apollo_api_key: str = ""
    claude_model: str = "claude-sonnet-4-5-20250929"
    slack_bot_token: str = ""
    slack_user_id: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/google/callback"
    google_drive_folder_id: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
