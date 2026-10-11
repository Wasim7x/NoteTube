import logging
from typing import Dict, Any, Optional
from app.services.llm.factory import create_llm_provider
from app.services.llm.ollama import check_ollama_startup
from app.config import settings

logger = logging.getLogger(__name__)

def test_provider_connection(
    provider: str,
    model: str,
    api_key: str = "",
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tests connectivity and model readiness for a chosen provider and model.
    Returns:
        {
            "success": bool,
            "provider": str,
            "model": str,
            "message": str,
            "details": Optional[Dict[str, Any]],
            "error": Optional[str]
        }
    """
    prov_clean = (provider or "").strip().lower()
    model_clean = (model or "").strip()
    key_clean = (api_key or "").strip()

    if not prov_clean:
        return {
            "success": False,
            "provider": prov_clean,
            "model": model_clean,
            "message": "Provider is required.",
            "error": "Provider is required."
        }

    # 1. Special validation for local Ollama
    if prov_clean == "ollama":
        target_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        startup_info = check_ollama_startup(
            base_url=target_url,
            configured_model=model_clean or settings.OLLAMA_MODEL
        )

        if not startup_info.get("service_running"):
            return {
                "success": False,
                "provider": "ollama",
                "model": startup_info.get("configured_model", ""),
                "message": f"Ollama service is not reachable at {target_url}.",
                "error": startup_info.get("message") or f"Could not connect to Ollama at {target_url}.",
                "details": startup_info
            }

        installed = startup_info.get("installed_models", [])
        active_model = startup_info.get("configured_model", "")
        # Check if model is installed or prefix matches
        has_model = any(
            active_model.lower() == m.lower() or
            active_model.lower() in m.lower() or
            m.lower().startswith(active_model.lower())
            for m in installed
        )

        if not has_model and installed:
            return {
                "success": False,
                "provider": "ollama",
                "model": active_model,
                "message": f"Model '{active_model}' is not installed in Ollama.",
                "error": f"Model '{active_model}' not found in installed models ({', '.join(installed[:5])}). Run: ollama pull {active_model}",
                "details": startup_info
            }

        return {
            "success": True,
            "provider": "ollama",
            "model": active_model,
            "message": f"Ollama is running at {target_url} with model '{active_model}' ready.",
            "details": startup_info
        }

    # 2. Validation for Cloud Providers (Gemini, OpenAI, Anthropic, Groq, OpenRouter)
    if not key_clean:
        return {
            "success": False,
            "provider": prov_clean,
            "model": model_clean,
            "message": f"API key is required for {prov_clean.capitalize()}.",
            "error": f"Please provide a valid API key for {prov_clean.capitalize()}."
        }

    try:
        llm = create_llm_provider(
            provider=prov_clean,
            model=model_clean,
            api_key=key_clean
        )
        # Execute a minimal ping prompt
        ping_resp = llm.generate_content(
            system_prompt="You are a health check assistant. Reply with only 'OK'.",
            user_prompt="Ping",
            temperature=0.0,
            max_tokens=10
        )
        if ping_resp and len(ping_resp.strip()) > 0:
            return {
                "success": True,
                "provider": prov_clean,
                "model": llm.model_name,
                "message": f"Successfully connected to {prov_clean.capitalize()} using model '{llm.model_name}'.",
                "details": {"ping_response": ping_resp.strip()[:50]}
            }
        else:
            return {
                "success": False,
                "provider": prov_clean,
                "model": model_clean,
                "message": "Provider responded with empty output.",
                "error": "Provider responded with empty output."
            }

    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Connection test failed for {prov_clean} ({model_clean}): {err_msg}")
        return {
            "success": False,
            "provider": prov_clean,
            "model": model_clean,
            "message": f"Failed to connect to {prov_clean.capitalize()}.",
            "error": err_msg
        }
