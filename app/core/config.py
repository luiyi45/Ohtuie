from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "OHTUIE"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "placeholder_secret_key_change_me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "placeholder@gmail.com"
    SMTP_PASSWORD: str = "placeholder_password"
    EMAILS_FROM_NAME: str = "OHTUIE Management"
    EMAILS_FROM_EMAIL: str = "ohtuiemanagement@gmail.com"
    BREVO_API_KEY: str = "placeholder"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Debug info for Railway (only prints names of variables found)
import os
if os.getenv("RAILWAY_ENVIRONMENT"):
    print(f"--- Railway Startup Debug ---")
    print(f"DATABASE_URL found in environment: {'DATABASE_URL' in os.environ}")
    print(f"Settings.DATABASE_URL value is set: {settings.DATABASE_URL is not None}")
    print(f"-----------------------------")
