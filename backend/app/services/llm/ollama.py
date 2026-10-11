import logging
import re
import shutil
from typing import List, Optional, Tuple, Dict, Any
import json
import httpx

from app.config import settings
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

def get_installed_models(base_url: Optional[str] = None, timeout: float = 3.0) -> List[str]:
    """
    Fetch the list of model names currently installed in the local Ollama instance.
    Returns an empty list if Ollama is unreachable.
    """
    url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(f"{url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return models
    except Exception as e:
        logger.debug(f"Could not retrieve installed models from Ollama: {e}")
    return []

def check_ollama_startup(
    base_url: Optional[str] = None,
    configured_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform preflight validation checks on Ollama:
    1. Check whether Ollama is installed and accessible.
    2. Check whether the Ollama service is running.
    3. Retrieve the list of installed models.
    4. Verify that the configured model exists.
    5. If model is missing, return the exact `ollama pull MODEL_NAME` command.
    6. If Ollama is unavailable, show a clear error explaining how to start it.
    """
    target_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
    target_model = configured_model or settings.OLLAMA_MODEL

    cli_available = shutil.which("ollama") is not None
    result: Dict[str, Any] = {
        "cli_installed": cli_available,
        "service_running": False,
        "base_url": target_url,
        "configured_model": target_model,
        "installed_models": [],
        "model_exists": False,
        "status": "error",
        "message": "",
        "suggested_command": ""
    }

    # Step 1 & 2: Check whether Ollama service is accessible & running
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{target_url}/api/tags")
            if resp.status_code == 200:
                result["service_running"] = True
                data = resp.json()
                installed = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                result["installed_models"] = installed
            else:
                result["message"] = (
                    f"Ollama server responded with unexpected status code {resp.status_code} at {target_url}."
                )
                return result
    except (httpx.ConnectError, httpx.ConnectTimeout):
        result["message"] = (
            f"Ollama service is not accessible at {target_url}.\n"
            "To start Ollama on Windows:\n"
            "  1. Launch the Ollama desktop application from the Start Menu, or\n"
            "  2. Open a terminal and run:\n"
            "       ollama serve\n"
            "  If port 11434 is already in use, verify if another instance of Ollama is already active."
        )
        result["suggested_command"] = "ollama serve"
        return result
    except Exception as ex:
        result["message"] = f"Failed to connect to Ollama at {target_url}: {ex}"
        result["suggested_command"] = "ollama serve"
        return result

    # Step 3 & 4: Retrieve models and check if configured model exists
    installed_models = result["installed_models"]
    
    # Model matching: exact match, or match without :latest tag
    def match_model(configured: str, available_list: List[str]) -> bool:
        c = configured.strip().lower()
        for m in available_list:
            m_low = m.strip().lower()
            if c == m_low:
                return True
            # e.g. "qwen3.5" matches "qwen3.5:latest"
            if not ":" in c and m_low == f"{c}:latest":
                return True
            if not ":" in m_low and f"{m_low}:latest" == c:
                return True
        return False

    if match_model(target_model, installed_models):
        result["model_exists"] = True
        result["status"] = "ok"
        result["message"] = (
            f"Ollama is running at {target_url}. Configured model '{target_model}' is available."
        )
        return result

    # Step 5: Model missing - display exact pull command
    result["status"] = "model_missing"
    pull_cmd = f"ollama pull {target_model}"
    result["suggested_command"] = pull_cmd
    installed_str = ", ".join(installed_models) if installed_models else "None"
    result["message"] = (
        f"Configured model '{target_model}' is not installed in Ollama.\n"
        f"Installed models: {installed_str}\n"
        f"To download this model, run the following command in your terminal:\n"
        f"  {pull_cmd}"
    )
    return result


class OllamaProvider(LLMProvider):
    """
    Local LLM Provider Adapter communicating directly with Ollama's HTTP API.
    Does not require any cloud credentials or external internet connection.
    """
    def __init__(
        self,
        model: str = "",
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        api_key: str = ""
    ):
        self.model = (model.strip() if model and model.strip() else settings.OLLAMA_MODEL)
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.OLLAMA_TIMEOUT

    @property
    def provider_name(self) -> str:
        return "ollama"

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
        endpoint = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": True
        }

        try:
            full_content = ""
            timeout_cfg = httpx.Timeout(self.timeout, connect=30.0, read=self.timeout)
            with httpx.Client(timeout=timeout_cfg) as client:
                with client.stream("POST", endpoint, json=payload) as response:
                    if response.status_code == 404:
                        logger.error(f"Ollama model '{self.model}' not found (HTTP 404).")
                        raise ValueError(
                            f"Model '{self.model}' was not found in Ollama. "
                            f"Please pull it by running: ollama pull {self.model}"
                        )

                    if response.status_code != 200:
                        err_text = response.read().decode("utf-8", errors="replace")
                        logger.error(f"Ollama returned HTTP {response.status_code}: {err_text}")
                        raise ValueError(f"Ollama request failed (HTTP {response.status_code}): {err_text}")

                    for line in response.iter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                piece = chunk.get("message", {}).get("content", "")
                                full_content += piece
                                if chunk.get("done"):
                                    break
                            except Exception:
                                pass

            if not full_content or not full_content.strip():
                raise RuntimeError(f"Ollama model '{self.model}' returned an empty response.")

            # If the model uses thinking tags (e.g. reasoning models), strip them to leave clean markdown notes
            cleaned_content = re.sub(r"<think>[\s\S]*?</think>", "", full_content).strip()
            return cleaned_content or full_content.strip()

        except httpx.ConnectError:
            logger.error(f"Failed to connect to Ollama at {self.base_url}.")
            raise ValueError(
                f"Could not connect to Ollama service at {self.base_url}. "
                "Ensure Ollama is running. On Windows, launch the Ollama desktop app or run 'ollama serve' in PowerShell/CMD."
            )
        except httpx.TimeoutException:
            logger.error(f"Ollama generation timed out after {self.timeout}s.")
            raise ValueError(
                f"Ollama request timed out after {self.timeout} seconds. "
                f"Model '{self.model}' may need more time to load or process. "
                "Try using a faster model like 'qwen3:1.7b' or increase OLLAMA_TIMEOUT in .env."
            )
        except ValueError:
            raise
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Ollama generation error: {err_msg}")
            raise ValueError(f"Ollama generation failed: {err_msg}")
