from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.llm.registry import ModelOption, ProviderInfo

class ProvidersResponse(BaseModel):
    providers: List[ProviderInfo]

class GenerateNotesRequest(BaseModel):
    youtube_url: str
    provider: str = Field(..., description="LLM provider: gemini, openai, anthropic, groq, openrouter")
    model: str = Field(..., description="Model identifier or custom model name")
    api_key: str = Field(..., description="API key for the selected provider")

class VideoMetadata(BaseModel):
    id: str
    title: str
    thumbnail: str

class NotesData(BaseModel):
    title: str
    content: str

class GenerateNotesResponse(BaseModel):
    success: bool
    provider: Optional[str] = None
    model: Optional[str] = None
    video: Optional[VideoMetadata] = None
    notes: Optional[NotesData] = None
    error: Optional[str] = None
