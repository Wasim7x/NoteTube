import logging
from app.services.llm.base import LLMProvider
from app.services.llm.registry import (
    register_provider,
    get_registered_provider_class,
    PROVIDER_METADATA
)
from app.config import settings
from app.services.llm.gemini import GeminiProvider
from app.services.llm.openai import OpenAIProvider
from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.groq import GroqProvider
from app.services.llm.openrouter import OpenRouterProvider
from app.services.llm.ollama import OllamaProvider

logger = logging.getLogger(__name__)

# Register all out-of-the-box providers
register_provider("gemini", GeminiProvider)
register_provider("openai", OpenAIProvider)
register_provider("anthropic", AnthropicProvider)
register_provider("groq", GroqProvider)
register_provider("openrouter", OpenRouterProvider)
register_provider("ollama", OllamaProvider)

def create_llm_provider(provider: str, model: str, api_key: str = "") -> LLMProvider:
    """
    Factory function to instantiate an LLMProvider dynamically given
    the user's provider choice, model name, and API key.
    """
    if not provider or not provider.strip():
        raise ValueError("Provider must be specified.")
        
    provider_clean = provider.strip().lower()
    api_key_clean = api_key.strip() if api_key else ""
    
    # API key is only mandatory for cloud providers, not for local Ollama
    if provider_clean != "ollama" and not api_key_clean:
        raise ValueError(f"API key is required for {provider_clean.capitalize()}.")
        
    # If model is empty, default to provider's default model or settings.OLLAMA_MODEL
    model_clean = model.strip() if model and model.strip() else ""
    if not model_clean:
        if provider_clean == "ollama":
            model_clean = settings.OLLAMA_MODEL or PROVIDER_METADATA["ollama"].default_model
        elif provider_clean in PROVIDER_METADATA:
            model_clean = PROVIDER_METADATA[provider_clean].default_model
        
    if not model_clean:
        raise ValueError("Model name must be specified.")

    provider_cls = get_registered_provider_class(provider_clean)
    logger.info(f"Instantiating LLM provider={provider_clean} with model={model_clean}")
    
    if provider_clean == "ollama":
        return provider_cls(
            model=model_clean,
            base_url=settings.OLLAMA_BASE_URL,
            timeout=settings.OLLAMA_TIMEOUT,
            api_key=api_key_clean
        )
    
    return provider_cls(api_key=api_key_clean, model=model_clean)
