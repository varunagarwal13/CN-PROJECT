import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(WORKSPACE_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    NETMIRAGE_ENV: str = "development"
    DATABASE_URL: str = f"sqlite:///{WORKSPACE_ROOT}/netmirage.db"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,*"

    # Safety Policy
    ALLOWED_LAB_CIDRS: str = "10.0.10.0/24,10.0.20.0/24,10.0.30.0/24,10.0.40.0/24,10.0.50.0/24"
    ALLOWED_LAB_PORTS: str = "22,2222,53,80,8080,25,587"
    MAX_ACTIONS_PER_MINUTE: int = 30
    MAX_CONCURRENT_ACTIONS: int = 2
    MAX_RUN_DURATION_SECONDS: int = 600

    # AI Planner
    PLANNER_MODE: str = "deterministic_or_llm"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

settings = Settings()
