from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.llm.registry import ModelOption, ProviderInfo

class ProvidersResponse(BaseModel):
    providers: List[ProviderInfo]

class GenerateNotesRequest(BaseModel):
    youtube_url: str
    provider: str = Field(..., description="LLM provider: ollama, gemini, openai, anthropic, groq, openrouter")
    model: str = Field(default="", description="Model identifier or custom model name")
    api_key: str = Field(default="", description="API key for selected provider (optional for Ollama)")

class ChapterItem(BaseModel):
    chapter_id: Optional[str] = None
    title: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    timestamp_str: Optional[str] = None
    duration_str: Optional[str] = None
    is_ai_detected: Optional[bool] = False
    content: Optional[str] = None

class ChapterSlideItem(BaseModel):
    chapter_id: str
    chapter_index: int
    title: str
    start_time: float
    end_time: float
    duration: float
    timestamp_str: str
    extraction_timestamp: float
    extraction_timestamp_str: str
    image_url: Optional[str] = None
    status: str = "pending"  # pending, completed, failed
    error: Optional[str] = None
    slide_index: Optional[int] = None

class VideoSlidesResponse(BaseModel):
    video_id: str
    video_title: str
    status: str = "completed"  # completed, processing, no_chapters, failed, not_started
    has_chapters: bool = True
    message: Optional[str] = None
    total_chapters: int = 0
    extracted_slides: int = 0
    slides: List[ChapterSlideItem] = []
    ppt_download_url: Optional[str] = None
    error: Optional[str] = None

class ExtractSlidesRequest(BaseModel):
    video_id: str
    youtube_url: Optional[str] = None
    chapters: Optional[List[ChapterItem]] = None
    force: Optional[bool] = False

class VideoMetadata(BaseModel):
    id: str
    title: str
    thumbnail: str
    description: Optional[str] = None
    duration: Optional[int] = None
    chapters: Optional[List[ChapterItem]] = None
    channel: Optional[str] = None

class NotesData(BaseModel):
    title: str
    content: str

class GenerateNotesResponse(BaseModel):
    success: bool
    provider: Optional[str] = None
    model: Optional[str] = None
    fallback_used: Optional[bool] = False
    transcript_available: Optional[bool] = None
    transcript_language: Optional[str] = None
    transcript_language_code: Optional[str] = None
    transcript_generated: Optional[bool] = None
    video: Optional[VideoMetadata] = None
    notes: Optional[NotesData] = None
    chapters: Optional[List[ChapterItem]] = None
    overview_content: Optional[str] = None
    revision_content: Optional[str] = None
    error: Optional[str] = None

class ValidateProviderRequest(BaseModel):
    provider: str
    model: Optional[str] = ""
    api_key: Optional[str] = ""
    base_url: Optional[str] = None

class ValidateProviderResponse(BaseModel):
    success: bool
    provider: str
    model: str
    message: str
    error: Optional[str] = None
    details: Optional[dict] = None

class LoadVideoRequest(BaseModel):
    youtube_url: str

class LoadVideoResponse(BaseModel):
    success: bool
    video_id: str
    video: Optional[VideoMetadata] = None
    transcript_available: bool = False
    transcript_language: Optional[str] = None
    transcript_language_code: Optional[str] = None
    transcript_generated: Optional[bool] = None
    transcript_preview: Optional[str] = None
    transcript_char_count: int = 0
    has_chapters: bool = True
    total_chapters: int = 0
    chapters: List[ChapterItem] = []
    error: Optional[str] = None

class QuickSummaryRequest(BaseModel):
    video_id: str
    youtube_url: Optional[str] = None
    provider: str
    model: Optional[str] = ""
    api_key: Optional[str] = ""

class QuickSummaryResponse(BaseModel):
    success: bool
    video_id: str
    title: str
    summary: str
    key_takeaways: List[str] = []
    core_concepts: List[str] = []
    markdown_content: str
    provider: str
    model: str
    error: Optional[str] = None

class DetailedNotesRequest(BaseModel):
    video_id: str
    youtube_url: Optional[str] = None
    provider: str
    model: Optional[str] = ""
    api_key: Optional[str] = ""

class DetailedNotesResponse(BaseModel):
    success: bool
    video_id: str
    title: str
    overview: str
    markdown_content: str
    chapters: List[ChapterItem] = []
    revision_summary: Optional[str] = None
    external_research_used: bool = False
    provider: str
    model: str
    error: Optional[str] = None

class RAGQueryRequest(BaseModel):
    video_id: str
    query: str
    provider: Optional[str] = "ollama"
    model: Optional[str] = ""
    api_key: Optional[str] = ""

class RAGSourceChunk(BaseModel):
    chunk_id: str
    timestamp_str: str
    start_time: float
    end_time: float
    chapter_title: Optional[str] = None
    text: str
    score: float

class RAGQueryResponse(BaseModel):
    success: bool
    video_id: str
    query: str
    answer: str
    sources: List[RAGSourceChunk] = []
    grounded: bool = True
    error: Optional[str] = None

class RAGStatusResponse(BaseModel):
    indexed: bool
    video_id: str
    chunk_count: int = 0
    embedding_model: Optional[str] = None

