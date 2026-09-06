import logging
import anthropic
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key or not api_key.strip():
            raise ValueError("Anthropic API key is required.")
        self.client = anthropic.Anthropic(api_key=api_key.strip())
        self.model = model.strip() if model else "claude-3-7-sonnet-latest"

    @property
    def provider_name(self) -> str:
        return "anthropic"

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
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Anthropic messages return blocks
            text_blocks = [b.text for b in response.content if hasattr(b, 'text')]
            content = "".join(text_blocks)

            if not content:
                raise RuntimeError("Anthropic returned an empty response.")
            return content

        except anthropic.AuthenticationError:
            logger.error("Anthropic Authentication Error: Invalid API key provided.")
            raise ValueError("The provided Anthropic API key is invalid or unauthorized.")
        except anthropic.RateLimitError:
            logger.error("Anthropic Rate Limit Error.")
            raise ValueError("Anthropic has temporarily rate-limited this request or your account credits are exhausted.")
        except anthropic.NotFoundError:
            logger.error(f"Anthropic Model Error: Model '{self.model}' not found.")
            raise ValueError(f"The selected model '{self.model}' is not found or not accessible on your Anthropic account.")
        except anthropic.APIConnectionError:
            logger.error("Anthropic Connection Error.")
            raise ValueError("Could not connect to Anthropic API servers. Please check your network connection.")
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Anthropic Generation Error: {err_msg}")
            if "credit balance" in err_msg.lower():
                raise ValueError("Your Anthropic account has insufficient credits to complete this request.")
            raise ValueError(f"Anthropic request failed: {err_msg}")
