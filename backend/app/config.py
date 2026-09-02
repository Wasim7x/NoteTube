from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional

class Settings(BaseSettings):
    MODEL_PROVIDER: str = "gemini"
    MODEL_NAME: str = "gemini-3.6-flash"
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    LLM_FALLBACK_ENABLED: bool = True
    LLM_FALLBACK_PROVIDER: str = "groq"
    GROQ_FALLBACK_MODEL: str = "llama-3.3-70b-versatile"
    
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode='after')
    def validate_provider(self):
        provider = self.MODEL_PROVIDER.lower()
        if provider == "groq" and not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required when MODEL_PROVIDER=groq")
        if provider == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when MODEL_PROVIDER=gemini")
        if provider not in ["groq", "gemini"]:
            raise ValueError(f"Unsupported MODEL_PROVIDER: {provider}")
            
        if self.LLM_FALLBACK_ENABLED:
            fallback = self.LLM_FALLBACK_PROVIDER.lower()
            if fallback == "groq" and not self.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is required when LLM_FALLBACK_PROVIDER=groq")
                
        return self

settings = Settings()
