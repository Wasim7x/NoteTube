from pydantic import BaseModel, HttpUrl
from typing import Optional

class GenerateNotesRequest(BaseModel):
    youtube_url: str

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
    fallback_used: bool = False
    video: Optional[VideoMetadata] = None
    notes: Optional[NotesData] = None
    error: Optional[str] = None
