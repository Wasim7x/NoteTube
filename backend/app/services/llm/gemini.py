import logging
from google import genai
from google.genai import types
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key or not api_key.strip():
            raise ValueError("Google Gemini API key is required.")
        self.client = genai.Client(api_key=api_key.strip())
        self.model = model.strip() if model else "gemini-2.5-flash"

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self.model

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> str:
        try:
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
                raise RuntimeError("Google Gemini returned an empty response.")

            return response.text
        except Exception as e:
            err_str = str(e)
            logger.error(f"Gemini Generation Error: {err_str}")
            if "API_KEY_INVALID" in err_str or "api key not valid" in err_str.lower() or "400" in err_str and "key" in err_str.lower():
                raise ValueError("The provided Google Gemini API key is invalid or unauthorized.")
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "quota" in err_str.lower():
                raise ValueError("Google Gemini has temporarily rate-limited this request or your quota is exhausted.")
            if "NOT_FOUND" in err_str or "not found" in err_str.lower():
                raise ValueError(f"The selected model '{self.model}' is not available on Google Gemini.")
            raise ValueError(f"Gemini generation failed: {err_str}")