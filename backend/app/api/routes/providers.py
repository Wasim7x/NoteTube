from fastapi import APIRouter
from app.models.schemas import ProvidersResponse, ValidateProviderRequest, ValidateProviderResponse
from app.services.llm.registry import get_all_providers_info
from app.services.llm.connection_test import test_provider_connection

router = APIRouter()

@router.get("", response_model=ProvidersResponse)
async def list_providers():
    """
    Returns the list of supported LLM providers, their metadata,
    and available model presets.
    """
    return ProvidersResponse(providers=get_all_providers_info())

@router.post("/validate", response_model=ValidateProviderResponse)
async def validate_provider(request: ValidateProviderRequest):
    """
    Validates model configuration and tests live connectivity.
    For local Ollama, verifies service status and model presence.
    For cloud providers, sends a minimal test ping to confirm credentials.
    """
    result = test_provider_connection(
        provider=request.provider,
        model=request.model or "",
        api_key=request.api_key or "",
        base_url=request.base_url
    )
    return ValidateProviderResponse(**result)

