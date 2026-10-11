import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    QuickSummaryRequest,
    QuickSummaryResponse,
    DetailedNotesRequest,
    DetailedNotesResponse,
    ChapterItem
)
from app.services.video_service import video_job_service
from app.services.llm.factory import create_llm_provider
from app.services.summarization_service import SummarizationService
from app.services.youtube_service import YouTubeService

logger = logging.getLogger(__name__)

router = APIRouter()

def _extract_bullets_from_markdown(markdown_text: str, section_header: str) -> list:
    """Extracts bullet items following a specific section header."""
    results = []
    lines = markdown_text.splitlines()
    in_section = False
    for line in lines:
        s = line.strip()
        if s.startswith("#") and section_header.lower() in s.lower():
            in_section = True
            continue
        elif in_section and s.startswith("#"):
            break
        elif in_section and (s.startswith("- ") or s.startswith("* ")):
            item = s[2:].strip()
            if item:
                results.append(item)
    return results

@router.post("/quick-summary", response_model=QuickSummaryResponse)
async def generate_quick_summary(request: QuickSummaryRequest):
    """
    Option 1: Quick Summary.
    Generates a concise, high-speed overview from the video transcript.
    Reuses cached transcript to prevent video download or duplicate queries.
    """
    if not request.video_id or not request.video_id.strip():
        raise HTTPException(status_code=400, detail="video_id is required.")

    video_id = request.video_id.strip()

    # Retrieve video job from cache, or load via URL if provided
    job = video_job_service.get_cached_job(video_id)
    if not job:
        if request.youtube_url:
            job_resp = video_job_service.load_video(request.youtube_url)
            job = video_job_service.get_cached_job(video_id)
        else:
            raise HTTPException(status_code=404, detail="Video has not been loaded. Please load the video first.")

    video_data = job.get("video", {})
    transcript_text = job.get("transcript_full", "")
    chapters_raw = job.get("chapters", [])
    chapters = [ChapterItem(**c) for c in chapters_raw]

    if not transcript_text or len(transcript_text.strip()) < 50:
        # Fallback to description when transcript is empty
        transcript_text = f"Title: {video_data.get('title')}\nDescription: {video_data.get('description', '')}"

    try:
        llm = create_llm_provider(
            provider=request.provider,
            model=request.model or "",
            api_key=request.api_key or ""
        )
        summarizer = SummarizationService(provider=llm)

        duration_sec = float(video_data.get("duration") or 0.0)
        dur_str = YouTubeService.format_duration(duration_sec) if duration_sec > 0 else "N/A"

        md_output = summarizer.generate_quick_summary(
            title=video_data.get("title", "Educational Video"),
            duration_str=dur_str,
            transcript_text=transcript_text,
            chapters=chapters
        )

        takeaways = _extract_bullets_from_markdown(md_output, "Key Takeaways")
        concepts = _extract_bullets_from_markdown(md_output, "Core Concepts")

        return QuickSummaryResponse(
            success=True,
            video_id=video_id,
            title=video_data.get("title", "Quick Summary"),
            summary=md_output,
            key_takeaways=takeaways,
            core_concepts=concepts,
            markdown_content=md_output,
            provider=llm.provider_name,
            model=llm.model_name
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error generating quick summary for {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Quick summary generation failed: {str(e)}")

@router.post("/detailed-notes", response_model=DetailedNotesResponse)
async def generate_detailed_notes(request: DetailedNotesRequest):
    """
    Option 2: Detailed Notes.
    Generates comprehensive pedagogical study notes from the transcript.
    """
    if not request.video_id or not request.video_id.strip():
        raise HTTPException(status_code=400, detail="video_id is required.")

    video_id = request.video_id.strip()

    job = video_job_service.get_cached_job(video_id)
    if not job:
        if request.youtube_url:
            job_resp = video_job_service.load_video(request.youtube_url)
            job = video_job_service.get_cached_job(video_id)
        else:
            raise HTTPException(status_code=404, detail="Video has not been loaded. Please load the video first.")

    video_data = job.get("video", {})
    transcript_text = job.get("transcript_full", "")
    chapters_raw = job.get("chapters", [])
    chapters = [ChapterItem(**c) for c in chapters_raw]

    if not transcript_text or len(transcript_text.strip()) < 50:
        transcript_text = f"Title: {video_data.get('title')}\nDescription: {video_data.get('description', '')}"

    try:
        llm = create_llm_provider(
            provider=request.provider,
            model=request.model or "",
            api_key=request.api_key or ""
        )
        summarizer = SummarizationService(provider=llm)

        duration_sec = float(video_data.get("duration") or 0.0)
        dur_str = YouTubeService.format_duration(duration_sec) if duration_sec > 0 else "N/A"

        md_output = summarizer.generate_detailed_notes(
            title=video_data.get("title", "Detailed Notes"),
            duration_str=dur_str,
            transcript_text=transcript_text,
            chapters=chapters
        )

        return DetailedNotesResponse(
            success=True,
            video_id=video_id,
            title=video_data.get("title", "Detailed Study Notes"),
            overview=(video_data.get("description") or "")[:400],
            markdown_content=md_output,
            chapters=chapters,
            revision_summary=None,
            external_research_used=False,
            provider=llm.provider_name,
            model=llm.model_name
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error generating detailed notes for {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Detailed notes generation failed: {str(e)}")
