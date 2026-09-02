import logging
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class FallbackProvider(LLMProvider):
    def __init__(self, primary: LLMProvider, fallback: LLMProvider):
        self.primary = primary
        self.fallback = fallback
        self.active = primary
        self.fallback_used = False

    @property
    def provider_name(self) -> str:
        return self.active.provider_name

    @property
    def model_name(self) -> str:
        return self.active.model_name

    def _is_retryable_error(self, e: Exception) -> bool:
        error_str = str(e).lower()
        
        # General checks for HTTP status codes that suggest rate limits or server errors
        retryable_keywords = [
            "429", "resource_exhausted", "resource exhausted", "rate limit", 
            "quota exceeded", "quota", "503", "service unavailable", 
            "504", "timeout"
        ]
        
        # Do not fallback on simple 400 Bad Request, API_KEY_INVALID or unsupported model
        if "api_key_invalid" in error_str or "unsupported" in error_str or "unavailable" in error_str and "model" in error_str:
            return False

        for keyword in retryable_keywords:
            if keyword in error_str:
                return True
                
        return False

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> str:
        try:
            return self.active.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            if not self.fallback_used and self._is_retryable_error(e):
                logger.error(f"{self.primary.provider_name.capitalize()} API Error: {str(e)}")
                logger.warning(f"{self.primary.provider_name.capitalize()} quota/credits exhausted or service unavailable.")
                logger.info("Fallback enabled: true")
                logger.info(f"Fallback Provider: {self.fallback.provider_name}")
                logger.info("Generating notes using fallback provider")
                
                self.active = self.fallback
                self.fallback_used = True
                
                # Retry with fallback provider
                result = self.active.generate_content(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.info("Fallback notes generated successfully")
                return result
            
            # If fallback already used or non-retryable error, re-raise
            raise
