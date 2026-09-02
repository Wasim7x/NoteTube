from app.models.schemas import GenerateNotesResponse, NotesData
from app.services.youtube_service import youtube_service
from app.services.transcript_service import transcript_service
from app.services.summarization_service import SummarizationService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class NotesService:
    @staticmethod
    def generate(url: str) -> GenerateNotesResponse:
        try:
            logger.info(f"Fetching metadata for {url}")
            metadata = youtube_service.get_video_metadata(url)
            
            logger.info(f"Fetching transcript for {metadata.id}")
            transcript = transcript_service.get_transcript(metadata.id)
            
            if not transcript or len(transcript.strip()) < 50:
                return GenerateNotesResponse(
                    success=False,
                    error="Transcript is empty or too short."
                )
                
            # Instantiate per-request to ensure thread-safety of Fallback state
            summarization_service = SummarizationService()
                
            logger.info(f"LLM Provider: {summarization_service.provider.provider_name}")
            logger.info(f"LLM Model: {summarization_service.provider.model_name}")
            logger.info(f"Generating notes (transcript length: {len(transcript)})")
            
            markdown_notes = summarization_service.generate_notes(transcript)
            logger.info("Notes generated successfully")
            
            # Check if fallback was used via FallbackProvider attribute, if it exists
            fallback_used = getattr(summarization_service.provider, "fallback_used", False)
            
            # Extract title from markdown if available (starts with #)
            notes_title = metadata.title
            first_line = markdown_notes.split('\n')[0].strip()
            if first_line.startswith('# '):
                notes_title = first_line[2:].strip()
            
            notes_data = NotesData(
                title=notes_title,
                content=markdown_notes
            )
            
            return GenerateNotesResponse(
                success=True,
                provider=summarization_service.provider.provider_name,
                model=summarization_service.provider.model_name,
                fallback_used=fallback_used,
                video=metadata,
                notes=notes_data
            )
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating notes: {error_str}")
            
            # Return our custom validation messages directly
            if "configured Gemini model is unavailable" in error_str or "Transcript is empty" in error_str:
                clean_error = error_str
            else:
                if getattr(settings, "LLM_FALLBACK_ENABLED", False):
                    clean_error = "The AI providers are currently unavailable. Please try again later."
                else:
                    clean_error = "The configured AI provider is currently unavailable and no fallback provider is configured."
            
            return GenerateNotesResponse(
                success=False,
                error=clean_error
            )

notes_service = NotesService()
