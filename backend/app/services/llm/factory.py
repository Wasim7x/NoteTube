import logging
from app.services.llm.base import LLMProvider
from app.services.llm.registry import (
    register_provider,
    get_registered_provider_class,
    PROVIDER_METADATA
)
from app.services.llm.gemini import GeminiProvider
from app.services.llm.openai import OpenAIProvider
from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.groq import GroqProvider
from app.services.llm.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

# Register all out-of-the-box providers
register_provider("gemini", GeminiProvider)
register_provider("openai", OpenAIProvider)
register_provider("anthropic", AnthropicProvider)
register_provider("groq", GroqProvider)
register_provider("openrouter", OpenRouterProvider)

def create_llm_provider(provider: str, model: str, api_key: str) -> LLMProvider:
    """
    Factory function to instantiate an LLMProvider dynamically given
    the user's provider choice, model name, and API key.
    """
    if not provider or not provider.strip():
        raise ValueError("Provider must be specified.")
        
    provider_clean = provider.strip().lower()
    
    if not api_key or not api_key.strip():
        raise ValueError(f"API key is required for {provider_clean.capitalize()}.")
        
    api_key_clean = api_key.strip()
    
    # If model is empty, default to provider's default model if available
    model_clean = model.strip() if model and model.strip() else ""
    if not model_clean and provider_clean in PROVIDER_METADATA:
        model_clean = PROVIDER_METADATA[provider_clean].default_model
        
    if not model_clean:
        raise ValueError("Model name must be specified.")

    provider_cls = get_registered_provider_class(provider_clean)
    logger.info(f"Instantiating LLM provider={provider_clean} with model={model_clean}")
    
    return provider_cls(api_key=api_key_clean, model=model_clean)
