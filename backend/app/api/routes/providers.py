from fastapi import APIRouter
from app.models.schemas import ProvidersResponse
from app.services.llm.registry import get_all_providers_info

router = APIRouter()

@router.get("", response_model=ProvidersResponse)
async def list_providers():
    """
    Returns the list of supported LLM providers, their metadata,
    and available model presets.
    """
    return ProvidersResponse(providers=get_all_providers_info())
