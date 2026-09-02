from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from app.utils.text_processing import clean_text
import logging

logger = logging.getLogger(__name__)

class TranscriptService:
    @staticmethod
    def get_transcript(video_id: str) -> str:
        """
        Fetches the transcript for a given YouTube video ID.
        Attempts to get manual first, then generated. Prefers English.
        """
        api = YouTubeTranscriptApi()
        
        try:
            transcript_list = api.list(video_id)
        except Exception as e:
            logger.error(f"ERROR | Transcript extraction failed | {str(e)}")
            raise Exception("Unable to retrieve a transcript for this video. The video may not have captions available.")

        try:
            # Try to fetch English manually created transcript
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
            except:
                # Fallback to English generated transcript
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except:
                    # Fallback to any transcript and translate to English
                    transcript = next(iter(transcript_list))
                    if transcript.language_code != 'en':
                        transcript = transcript.translate('en')
            
            transcript_data = transcript.fetch()
            logger.info("Transcript retrieved successfully")
            
            logger.info("Cleaning transcript")
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript_data)
            
            return clean_text(formatted_transcript)
            
        except Exception as e:
            logger.error(f"ERROR | Transcript extraction failed | {str(e)}")
            raise Exception("Unable to retrieve a transcript for this video. The video may not have captions available.")

transcript_service = TranscriptService()
