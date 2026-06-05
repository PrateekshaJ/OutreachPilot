"""
Application configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized settings for the SynkSpace Outreach Bot backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    mongodb_uri: str
    mongodb_db: str = "synkspace_outreach"

    zoho_email: str = ""
    zoho_password: str = ""
    smtp_server: str = "smtp.zoho.com"
    smtp_port: int = 587

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()

print("MONGO URL LOADED:", settings.mongodb_uri)

def get_settings():
    return settings