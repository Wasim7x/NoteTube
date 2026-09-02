from app.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.groq import GroqProvider
from app.services.llm.gemini import GeminiProvider
from app.services.llm.fallback import FallbackProvider

def _create_provider(name: str) -> LLMProvider:
    if name == "groq":
        return GroqProvider(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_FALLBACK_MODEL if settings.MODEL_PROVIDER.lower() != "groq" else settings.MODEL_NAME
        )
    elif name == "gemini":
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.MODEL_NAME
        )
    else:
        raise ValueError(f"Unsupported LLM Provider configured: {name}")

def get_llm_provider() -> LLMProvider:
    primary_provider = _create_provider(settings.MODEL_PROVIDER.lower())
    
    if settings.LLM_FALLBACK_ENABLED and settings.MODEL_PROVIDER.lower() != settings.LLM_FALLBACK_PROVIDER.lower():
        fallback_provider = _create_provider(settings.LLM_FALLBACK_PROVIDER.lower())
        return FallbackProvider(primary=primary_provider, fallback=fallback_provider)
        
    return primary_provider
