import logging
import openai
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key or not api_key.strip():
            raise ValueError("OpenAI API key is required.")
        self.client = openai.OpenAI(api_key=api_key.strip())
        self.model = model.strip() if model else "gpt-4o-mini"

    @property
    def provider_name(self) -> str:
        return "openai"

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
            # For reasoning models (o1, o3-mini), system message or temperature might need adjustment
            is_reasoning_model = self.model.startswith("o1") or self.model.startswith("o3")
            
            messages = []
            if is_reasoning_model:
                # o1 / o3 models use developer or user messages
                messages.append({"role": "user", "content": f"{system_prompt}\n\n---\n\n{user_prompt}"})
                extra_params = {}
            else:
                messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": user_prompt})
                extra_params = {
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **extra_params
            )

            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("OpenAI returned an empty response.")
            return content

        except openai.AuthenticationError:
            logger.error("OpenAI Authentication Error: Invalid API key provided.")
            raise ValueError("The provided OpenAI API key is invalid or unauthorized.")
        except openai.RateLimitError:
            logger.error("OpenAI Rate Limit Error: Quota exceeded or rate limit hit.")
            raise ValueError("OpenAI has temporarily rate-limited this request or your account quota is exhausted.")
        except openai.NotFoundError:
            logger.error(f"OpenAI Model Error: Model '{self.model}' not found.")
            raise ValueError(f"The selected model '{self.model}' is not available or not supported on your OpenAI account.")
        except openai.APIConnectionError:
            logger.error("OpenAI Connection Error.")
            raise ValueError("Could not connect to OpenAI API servers. Please check your network connection.")
        except Exception as e:
            err_msg = str(e)
            logger.error(f"OpenAI Generation Error: {err_msg}")
            if "maximum context length" in err_msg.lower():
                raise ValueError("The transcript exceeds the context window for this OpenAI model.")
            raise ValueError(f"OpenAI request failed: {err_msg}")
