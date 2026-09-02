from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider (e.g. 'groq', 'gemini')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the model being used."""
        pass

    @abstractmethod
    def generate_content(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 4000) -> str:
        """
        Generate text content from the LLM provider.
        """
        pass
