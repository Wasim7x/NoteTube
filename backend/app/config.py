from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env path: check current working directory or backend directory
_backend_dir = Path(__file__).resolve().parent.parent
_env_files = [".env", str(_backend_dir / ".env")]

class Settings(BaseSettings):
    FRONTEND_URL: str = "http://localhost:5173"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # LLM Settings
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:1.7b"
    OLLAMA_TIMEOUT: float = 120.0

    model_config = SettingsConfigDict(
        env_file=_env_files,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

