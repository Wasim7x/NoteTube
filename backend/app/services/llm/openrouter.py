import logging
import openai
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key or not api_key.strip():
            raise ValueError("OpenRouter API key is required.")
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key.strip(),
            default_headers={
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "NoteTube AI"
            }
        )
        self.model = model.strip() if model else "deepseek/deepseek-chat"

    @property
    def provider_name(self) -> str:
        return "openrouter"

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
                raise RuntimeError("OpenRouter returned an empty response.")
            return content

        except openai.AuthenticationError:
            logger.error("OpenRouter Authentication Error: Invalid API key provided.")
            raise ValueError("The provided OpenRouter API key is invalid or rejected.")
        except openai.RateLimitError:
            logger.error("OpenRouter Rate Limit Error.")
            raise ValueError("OpenRouter rate-limited this request or your balance is insufficient.")
        except openai.NotFoundError:
            logger.error(f"OpenRouter Model Error: Model '{self.model}' not found.")
            raise ValueError(f"The selected model '{self.model}' is not available on OpenRouter.")
        except openai.APIConnectionError:
            logger.error("OpenRouter Connection Error.")
            raise ValueError("Could not connect to OpenRouter API servers. Please check your network connection.")
        except Exception as e:
            err_msg = str(e)
            logger.error(f"OpenRouter Generation Error: {err_msg}")
            if "credit" in err_msg.lower() or "balance" in err_msg.lower():
                raise ValueError("Insufficient OpenRouter credits or balance.")
            raise ValueError(f"OpenRouter request failed: {err_msg}")
