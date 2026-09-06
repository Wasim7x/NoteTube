import logging
import groq
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key or not api_key.strip():
            raise ValueError("Groq API key is required.")
        self.client = groq.Groq(api_key=api_key.strip())
        self.model = model.strip() if model else "llama-3.3-70b-versatile"

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self.model

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("Groq returned an empty response.")
            return content

        except groq.AuthenticationError:
            logger.error("Groq Authentication Error: Invalid API key provided.")
            raise ValueError("The provided Groq API key is invalid or rejected.")
        except groq.RateLimitError:
            logger.error("Groq Rate Limit Error.")
            raise ValueError("Groq has temporarily rate-limited this request. Please try again in a few moments.")
        except groq.NotFoundError:
            logger.error(f"Groq Model Error: Model '{self.model}' not found.")
            raise ValueError(f"The selected model '{self.model}' is not available on Groq.")
        except groq.APIConnectionError:
            logger.error("Groq Connection Error.")
            raise ValueError("Could not connect to Groq API servers. Please check your network connection.")
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Groq Generation Error: {err_msg}")
            raise ValueError(f"Groq request failed: {err_msg}")
