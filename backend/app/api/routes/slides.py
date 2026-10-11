import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.models.schemas import ExtractSlidesRequest, VideoSlidesResponse
from app.services.slide_service import slide_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract", response_model=VideoSlidesResponse)
async def extract_chapter_slides(request: ExtractSlidesRequest):
    """
    Extracts representative frames from YouTube chapters (5 seconds before chapter end)
    and compiles a downloadable 16:9 PowerPoint presentation.
    """
    if not request.video_id or not request.video_id.strip():
        raise HTTPException(status_code=400, detail="video_id is required.")

    try:
        response = slide_service.extract_slides(
            video_id=request.video_id.strip(),
            youtube_url=request.youtube_url.strip() if request.youtube_url else None,
            chapters=request.chapters,
            force=bool(request.force)
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error during slide extraction for {request.video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Slide extraction failed: {str(e)}")


@router.get("/{video_id}", response_model=VideoSlidesResponse)
async def get_chapter_slides(video_id: str):
    """
    Retrieves status, slide mappings, and PowerPoint download URL for a video.
    """
    try:
        clean_id = slide_service.sanitize_id(video_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    slides_info = slide_service.get_slides(clean_id)
    if not slides_info:
        return VideoSlidesResponse(
            video_id=clean_id,
            video_title="Unknown",
            status="not_started",
            has_chapters=True,
            message="Slides have not been extracted yet for this video.",
            total_chapters=0,
            extracted_slides=0,
            slides=[]
        )

    return slides_info


@router.get("/{video_id}/images/{chapter_id}")
async def get_slide_image(video_id: str, chapter_id: str):
    """
    Serves the extracted slide frame image for the specified chapter.
    """
    try:
        clean_vid = slide_service.sanitize_id(video_id)
        clean_cid = slide_service.sanitize_id(chapter_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    img_path = slide_service.get_slide_image_path(clean_vid, clean_cid)
    if not img_path or not img_path.exists():
        raise HTTPException(status_code=404, detail="Slide image not found.")

    return FileResponse(
        path=str(img_path),
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=86400"}
    )


@router.get("/{video_id}/download-ppt")
async def download_presentation(video_id: str):
    """
    Downloads the generated PowerPoint (.pptx) presentation.
    """
    try:
        clean_vid = slide_service.sanitize_id(video_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    ppt_path = slide_service.get_presentation_path(clean_vid)
    if not ppt_path or not ppt_path.exists():
        raise HTTPException(status_code=404, detail="PowerPoint presentation not found. Please extract slides first.")

    # Get title for filename
    cached = slide_service.get_slides(clean_vid)
    raw_title = cached.video_title if cached and cached.video_title else "presentation"
    filename = f"{slide_service.sanitize_filename(raw_title)}_chapter_slides.pptx"

    return FileResponse(
        path=str(ppt_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
