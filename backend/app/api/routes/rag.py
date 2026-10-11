import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import RAGQueryRequest, RAGQueryResponse, RAGStatusResponse
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ask", response_model=RAGQueryResponse)
async def ask_video_chatbot(request: RAGQueryRequest):
    """
    Answers a question grounded in the video's transcript using semantic RAG.
    Returns the grounded answer with timestamp citations and source chunks.
    """
    if not request.video_id or not request.video_id.strip():
        raise HTTPException(status_code=400, detail="video_id is required.")
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Question query cannot be empty.")

    video_id = request.video_id.strip()
    query = request.query.strip()

    try:
        response = rag_service.answer_query(
            video_id=video_id,
            query=query,
            provider=request.provider,
            model=request.model or "",
            api_key=request.api_key or ""
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error querying RAG for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@router.get("/status/{video_id}", response_model=RAGStatusResponse)
async def get_rag_status(video_id: str):
    """
    Checks if a persistent RAG index exists for the video.
    """
    clean_id = "".join(c for c in video_id if c.isalnum() or c in "-_")[:64]
    index_file = rag_service.data_dir / clean_id / "index.json"

    if index_file.exists():
        import json
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return RAGStatusResponse(
                indexed=True,
                video_id=clean_id,
                chunk_count=data.get("chunk_count", 0),
                embedding_model=data.get("embedding_type")
            )
        except Exception:
            pass

    return RAGStatusResponse(
        indexed=False,
        video_id=clean_id,
        chunk_count=0,
        embedding_model=None
    )
