from fastapi import APIRouter, HTTPException
from app.models.schemas import GenerateNotesRequest, GenerateNotesResponse
from app.services.notes_service import notes_service

router = APIRouter()

@router.post("/generate", response_model=GenerateNotesResponse)
async def generate_notes(request: GenerateNotesRequest):
    # Perform input validation
    if not request.youtube_url or not request.youtube_url.strip():
        raise HTTPException(status_code=400, detail="YouTube URL is required.")
    if not request.provider or not request.provider.strip():
        raise HTTPException(status_code=400, detail="Model provider is required.")
    if not request.api_key or not request.api_key.strip():
        raise HTTPException(status_code=400, detail="API key is required.")

    response = notes_service.generate(
        url=request.youtube_url.strip(),
        provider=request.provider.strip(),
        model=request.model.strip() if request.model else "",
        api_key=request.api_key.strip()
    )
    
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error or "Failed to generate notes.")
        
    return response
