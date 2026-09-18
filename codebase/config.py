"""
config.py — App settings loaded from .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    OPENAI_API_KEY: str
    TAVILY_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    DATABASE_URL: str = "sqlite:///./scriptscout.db"


settings = Settings()
