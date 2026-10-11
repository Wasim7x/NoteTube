import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import GenerateNotesRequest, GenerateNotesResponse
from app.services.notes_service import notes_service

router = APIRouter()

def _validate_request(request: GenerateNotesRequest):
    if not request.youtube_url or not request.youtube_url.strip():
        raise HTTPException(status_code=400, detail="YouTube URL is required.")
    if not request.provider or not request.provider.strip():
        raise HTTPException(status_code=400, detail="Model provider is required.")
    provider_clean = request.provider.strip().lower()
    if provider_clean != "ollama" and (not request.api_key or not request.api_key.strip()):
        raise HTTPException(status_code=400, detail="API key is required.")

@router.post("/generate", response_model=GenerateNotesResponse)
async def generate_notes(request: GenerateNotesRequest):
    """
    Standard synchronous notes generation endpoint.
    Returns the complete structured notes response once generation finishes.
    """
    _validate_request(request)

    response = notes_service.generate(
        url=request.youtube_url.strip(),
        provider=request.provider.strip(),
        model=request.model.strip() if request.model else "",
        api_key=request.api_key.strip() if request.api_key else ""
    )
    
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error or "Failed to generate notes.")
        
    return response

@router.post("/generate-stream")
async def generate_notes_stream(request: GenerateNotesRequest):
    """
    Server-Sent Events (SSE) streaming endpoint for progressive note generation.
    Emits real-time progress events and completed chapters as they become available.
    """
    _validate_request(request)

    def event_stream():
        try:
            for event in notes_service.generate_stream(
                url=request.youtube_url.strip(),
                provider=request.provider.strip(),
                model=request.model.strip() if request.model else "",
                api_key=request.api_key.strip() if request.api_key else ""
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            err_data = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(err_data)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
