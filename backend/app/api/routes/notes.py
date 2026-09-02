from fastapi import APIRouter, HTTPException
from app.models.schemas import GenerateNotesRequest, GenerateNotesResponse
from app.services.notes_service import notes_service
from app.config import settings

router = APIRouter()

@router.post("/generate", response_model=GenerateNotesResponse)
async def generate_notes(request: GenerateNotesRequest):
    response = notes_service.generate(request.youtube_url)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response
