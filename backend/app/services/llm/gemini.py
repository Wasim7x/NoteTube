from google import genai
from google.genai import types
import logging

from app.services.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self._model_verified = False

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self.model

    def _verify_model(self):
        if self._model_verified:
            return
            
        logger = logging.getLogger(__name__)
        
        try:
            # Dynamically verify if the configured model exists and supports generation
            m = self.client.models.get(model=self.model)
            if "generateContent" not in (m.supported_actions or []):
                 raise ValueError(f"The configured Gemini model '{self.model}' does not support text generation (generateContent).")
            self._model_verified = True
        except Exception as e:
            if isinstance(e, ValueError) and "does not support" in str(e):
                logger.error(f"Gemini Model Verification Error: {str(e)}")
                raise
            logger.error(f"Gemini Model Verification Error: {str(e)}")
            raise ValueError(f"The configured Gemini model is unavailable.\nPlease check MODEL_NAME in your environment configuration.")

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> str:
        
        self._verify_model()
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return response.text