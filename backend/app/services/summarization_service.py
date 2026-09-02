from app.prompts.notes_prompt import NOTES_SYSTEM_PROMPT, CHUNK_SUMMARY_PROMPT, FINAL_MERGE_PROMPT
from app.services.llm.factory import get_llm_provider
import logging

logger = logging.getLogger(__name__)

class SummarizationService:
    def __init__(self):
        self.provider = get_llm_provider()
        self.chunk_size = 15000  # approximate character limit per chunk for processing

    def chunk_text(self, text: str) -> list[str]:
        """Splits transcript into manageable chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_len = 0
        
        # Approximate 1 word = 5 chars
        for word in words:
            if current_len + len(word) > self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_len = len(word)
            else:
                current_chunk.append(word)
                current_len += len(word) + 1 # +1 for space
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def process_single_chunk(self, transcript: str) -> str:
        """Processes a single transcript chunk directly into notes."""
        return self.provider.generate_content(
            system_prompt=NOTES_SYSTEM_PROMPT,
            user_prompt=f"Transcript:\n{transcript}",
            temperature=0.3,
            max_tokens=4000
        )

    def summarize_chunk(self, chunk: str) -> str:
        """Extracts information from a chunk to be merged later."""
        return self.provider.generate_content(
            system_prompt="You are an assistant that extracts key technical and educational information from transcripts.",
            user_prompt=CHUNK_SUMMARY_PROMPT.format(text=chunk),
            temperature=0.2,
            max_tokens=2000
        )

    def merge_summaries(self, summaries: list[str]) -> str:
        """Merges multiple chunk summaries into final notes."""
        combined_text = "\n\n---\n\n".join(summaries)
        return self.provider.generate_content(
            system_prompt=NOTES_SYSTEM_PROMPT,
            user_prompt=FINAL_MERGE_PROMPT.format(text=combined_text),
            temperature=0.3,
            max_tokens=4000
        )

    def generate_notes(self, transcript: str) -> str:
        """Main entry point to generate notes from transcript."""
        chunks = self.chunk_text(transcript)
        
        if len(chunks) == 1:
            # For short videos, generate directly
            return self.process_single_chunk(chunks[0])
        
        # For long videos, chunk and map-reduce
        logger.info(f"Transcript is long. Splitting into {len(chunks)} chunks.")
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            summary = self.summarize_chunk(chunk)
            chunk_summaries.append(summary)
            
        logger.info("Merging summaries...")
        return self.merge_summaries(chunk_summaries)
