import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import LoadVideoRequest, LoadVideoResponse
from app.services.video_service import video_job_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/load", response_model=LoadVideoResponse)
async def load_video(request: LoadVideoRequest):
    """
    Validates YouTube URL, retrieves video metadata, extracts transcript once,
    and returns durable video context for downstream processing modes and RAG chatbot.
    """
    if not request.youtube_url or not request.youtube_url.strip():
        raise HTTPException(status_code=400, detail="YouTube URL is required.")

    try:
        response = video_job_service.load_video(request.youtube_url.strip())
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error loading video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load video: {str(e)}")

@router.get("/{video_id}", response_model=LoadVideoResponse)
async def get_video_job(video_id: str):
    """
    Retrieves cached video job for video_id if available.
    """
    clean_id = "".join(c for c in video_id if c.isalnum() or c in "-_")[:64]
    cached = video_job_service.get_cached_job(clean_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Video job not found. Please load the video first.")

    from app.models.schemas import VideoMetadata, ChapterItem
    return LoadVideoResponse(
        success=True,
        video_id=clean_id,
        video=VideoMetadata(**cached["video"]),
        transcript_available=cached.get("transcript_available", False),
        transcript_language=cached.get("transcript_language"),
        transcript_language_code=cached.get("transcript_language_code"),
        transcript_generated=cached.get("transcript_generated"),
        transcript_preview=cached.get("transcript_preview"),
        transcript_char_count=cached.get("transcript_char_count", 0),
        has_chapters=cached.get("has_chapters", True),
        total_chapters=len(cached.get("chapters", [])),
        chapters=[ChapterItem(**c) for c in cached.get("chapters", [])]
    )
