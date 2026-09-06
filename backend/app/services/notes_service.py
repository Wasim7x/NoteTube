from app.models.schemas import GenerateNotesResponse, NotesData
from app.services.youtube_service import youtube_service
from app.services.transcript_service import transcript_service
from app.services.summarization_service import SummarizationService
from app.services.llm.factory import create_llm_provider
import logging

logger = logging.getLogger(__name__)

class NotesService:
    @staticmethod
    def generate(url: str, provider: str, model: str, api_key: str) -> GenerateNotesResponse:
        try:
            # 1. Initialize LLM Provider with user configuration
            llm_provider = create_llm_provider(
                provider=provider,
                model=model,
                api_key=api_key
            )
            
            # 2. Fetch YouTube metadata
            logger.info(f"Fetching metadata for {url}")
            metadata = youtube_service.get_video_metadata(url)
            
            # 3. Fetch transcript
            logger.info(f"Fetching transcript for video {metadata.id}")
            transcript = transcript_service.get_transcript(metadata.id)
            
            if not transcript or len(transcript.strip()) < 50:
                return GenerateNotesResponse(
                    success=False,
                    error="The transcript for this video is empty or too short to generate notes."
                )
                
            # 4. Summarize using the selected dynamic provider
            summarization_service = SummarizationService(provider=llm_provider)
                
            logger.info(f"LLM Provider: {llm_provider.provider_name}")
            logger.info(f"LLM Model: {llm_provider.model_name}")
            logger.info(f"Generating notes (transcript length: {len(transcript)} chars)")
            
            markdown_notes = summarization_service.generate_notes(transcript)
            logger.info("Notes generated successfully")
            
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
                provider=llm_provider.provider_name,
                model=llm_provider.model_name,
                video=metadata,
                notes=notes_data
            )
            
        except ValueError as ve:
            # Clean user-friendly error from validation or provider adapter
            error_str = str(ve)
            logger.warning(f"Validation/Provider error: {error_str}")
            return GenerateNotesResponse(
                success=False,
                error=error_str
            )
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating notes: {error_str}")
            
            # Sanitize unexpected error messages so no API key fragments or traces leak
            if "youtube" in error_str.lower() or "transcript" in error_str.lower():
                clean_error = error_str
            else:
                clean_error = f"Failed to generate notes: {error_str}"
            
            return GenerateNotesResponse(
                success=False,
                error=clean_error
            )

notes_service = NotesService()
