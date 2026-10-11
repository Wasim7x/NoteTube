import logging
import re
from typing import List, Tuple, Optional, Callable, Dict, Any
from app.prompts.notes_prompt import (
    NOTES_SYSTEM_PROMPT,
    CHUNK_SUMMARY_PROMPT,
    FINAL_MERGE_PROMPT,
    METADATA_FALLBACK_PROMPT,
    VIDEO_OVERVIEW_PROMPT,
    CHAPTER_NOTES_PROMPT,
    CHAPTER_CHUNK_SUMMARY_PROMPT,
    FINAL_REVISION_PROMPT,
    FALLBACK_CHAPTER_NOTES_PROMPT,
    QUICK_SUMMARY_PROMPT,
    DETAILED_NOTES_PROMPT
)
from app.services.llm.base import LLMProvider
from app.models.schemas import VideoMetadata, ChapterItem
from app.services.youtube_service import YouTubeService

logger = logging.getLogger(__name__)

class SummarizationService:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.chunk_size = 8000  # character limit per chunk for local LLM context sweet spot

    def chunk_text(self, text: str, max_chars: Optional[int] = None) -> List[str]:
        """Splits transcript into manageable chunks respecting word boundaries."""
        limit = max_chars or self.chunk_size
        words = text.split()
        chunks = []
        current_chunk = []
        current_len = 0
        
        for word in words:
            if current_len + len(word) > limit:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_len = len(word)
            else:
                current_chunk.append(word)
                current_len += len(word) + 1
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks if chunks else [text]

    # -------------------------------------------------------------
    # Legacy Single / Map-Reduce Methods (Preserved for compatibility)
    # -------------------------------------------------------------
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

    def merge_summaries(self, summaries: List[str]) -> str:
        """Merges multiple chunk summaries into final notes."""
        combined_text = "\n\n---\n\n".join(summaries)
        return self.provider.generate_content(
            system_prompt=NOTES_SYSTEM_PROMPT,
            user_prompt=FINAL_MERGE_PROMPT.format(text=combined_text),
            temperature=0.3,
            max_tokens=4000
        )

    def generate_notes(self, transcript: str) -> str:
        """Main entry point to generate notes from transcript (legacy mode)."""
        chunks = self.chunk_text(transcript, max_chars=15000)
        
        if len(chunks) == 1:
            return self.process_single_chunk(chunks[0])
        
        logger.info(f"Transcript is long. Splitting into {len(chunks)} chunks.")
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            summary = self.summarize_chunk(chunk)
            chunk_summaries.append(summary)
            
        logger.info("Merging summaries...")
        return self.merge_summaries(chunk_summaries)

    def generate_notes_from_fallback(
        self,
        title: str,
        channel: str = "",
        duration: str = "",
        chapters_text: str = "",
        description: str = ""
    ) -> str:
        """Legacy fallback synthesis."""
        logger.info(f"Generating notes via legacy fallback synthesis for '{title}'")
        fallback_prompt = METADATA_FALLBACK_PROMPT.format(
            title=title,
            channel=channel or "Unknown",
            duration=duration or "N/A",
            chapters=chapters_text or "No chapter timestamps listed.",
            description=description or "No description provided."
        )
        return self.provider.generate_content(
            system_prompt="You are an expert educator and technical writer creating structured notes from video syllabus and roadmap.",
            user_prompt=fallback_prompt,
            temperature=0.3,
            max_tokens=4000
        )

    # -------------------------------------------------------------
    # Chapter-by-Chapter Structured Generation Methods
    # -------------------------------------------------------------
    def generate_video_overview(
        self,
        title: str,
        duration_str: str,
        context: str
    ) -> str:
        """Generates Section A: Video Overview."""
        logger.info(f"Generating Video Overview for: {title}")
        prompt = VIDEO_OVERVIEW_PROMPT.format(
            title=title,
            duration=duration_str,
            context=context[:4000] if len(context) > 4000 else context
        )
        return self.provider.generate_content(
            system_prompt="You are an expert educator and technical curriculum designer.",
            user_prompt=prompt,
            temperature=0.25,
            max_tokens=2500
        )

    def generate_chapter_notes(
        self,
        chapter_num: int,
        chapter_title: str,
        timestamp_str: str,
        duration_str: str,
        transcript_text: str
    ) -> str:
        """
        Generates Section B: Chapter Notes for a single chapter.
        Uses map-and-reduce if chapter transcript is long (> 8000 characters).
        """
        logger.info(f"Generating Chapter {chapter_num}: {chapter_title} (length: {len(transcript_text)} chars)")
        clean_text = transcript_text.strip()
        
        # If chapter transcript is very long, use map-and-reduce
        if len(clean_text) > self.chunk_size:
            chunks = self.chunk_text(clean_text, max_chars=4000)
            logger.info(f"Chapter {chapter_num} is long ({len(clean_text)} chars). Splitting into {len(chunks)} sub-chunks.")
            sub_summaries = []
            for idx, c in enumerate(chunks):
                sub_prompt = CHAPTER_CHUNK_SUMMARY_PROMPT.format(
                    chapter_num=chapter_num,
                    chapter_title=chapter_title,
                    text=c
                )
                sub_summary = self.provider.generate_content(
                    system_prompt="You are a technical educator extracting key concepts and details from chapter transcripts.",
                    user_prompt=sub_prompt,
                    temperature=0.2,
                    max_tokens=1500
                )
                sub_summaries.append(sub_summary)
            
            combined_context = "\n\n".join(sub_summaries)
        else:
            combined_context = clean_text if clean_text else "No spoken dialogue recorded in this chapter interval."

        user_prompt = CHAPTER_NOTES_PROMPT.format(
            chapter_num=chapter_num,
            chapter_title=chapter_title,
            timestamp_str=timestamp_str,
            duration_str=duration_str,
            transcript=combined_context
        )

        return self.provider.generate_content(
            system_prompt="You are an expert educator and technical note-taker specializing in detailed chapter-by-chapter study guides.",
            user_prompt=user_prompt,
            temperature=0.25,
            max_tokens=3500
        )

    def generate_fallback_chapter_notes(
        self,
        chapter_num: int,
        chapter_title: str,
        timestamp_str: str,
        duration_str: str,
        context: str
    ) -> str:
        """Generates chapter notes from video syllabus when transcript is unavailable."""
        logger.info(f"Generating fallback notes for Chapter {chapter_num}: {chapter_title}")
        user_prompt = FALLBACK_CHAPTER_NOTES_PROMPT.format(
            chapter_num=chapter_num,
            chapter_title=chapter_title,
            timestamp_str=timestamp_str,
            duration_str=duration_str,
            context=context[:2000]
        )
        return self.provider.generate_content(
            system_prompt="You are an expert educator creating chapter curriculum notes from course syllabus.",
            user_prompt=user_prompt,
            temperature=0.25,
            max_tokens=2500
        )

    def generate_final_revision(
        self,
        title: str,
        all_chapters_summary: str
    ) -> str:
        """Generates Section C: Final Revision Section."""
        logger.info(f"Generating Final Revision Section for: {title}")
        user_prompt = FINAL_REVISION_PROMPT.format(
            title=title,
            all_chapters_summary=all_chapters_summary[:6000]
        )
        return self.provider.generate_content(
            system_prompt="You are an expert educator creating high-yield review guides and self-assessment quizzes.",
            user_prompt=user_prompt,
            temperature=0.25,
            max_tokens=3000
        )

    def build_full_markdown(
        self,
        overview_content: str,
        chapters: List[ChapterItem],
        revision_content: str
    ) -> str:
        """
        Combines Video Overview, all Chapter Notes, and Final Revision
        into one cohesive, beautifully formatted Markdown document.
        """
        sections = []
        if overview_content and overview_content.strip():
            sections.append(overview_content.strip())

        for ch in chapters:
            if ch.content and ch.content.strip():
                sections.append(ch.content.strip())

        if revision_content and revision_content.strip():
            sections.append(revision_content.strip())

        return "\n\n---\n\n".join(sections)

    def generate_quick_summary(
        self,
        title: str,
        duration_str: str,
        transcript_text: str,
        chapters: Optional[List[ChapterItem]] = None
    ) -> str:
        """
        Generates Option 1: Quick Summary from transcript.
        Prioritizes speed, low resource consumption, and high information density.
        """
        logger.info(f"Generating Quick Summary for video '{title}'")
        ch_list_str = "None"
        if chapters and len(chapters) > 0:
            ch_list_str = ", ".join([f"{c.title} ({c.timestamp_str or 'N/A'})" for c in chapters[:12]])

        # Limit transcript for quick summary to 12,000 characters for high speed
        bounded_transcript = transcript_text[:12000] if transcript_text else "No transcript text available."

        prompt = QUICK_SUMMARY_PROMPT.format(
            title=title,
            duration=duration_str,
            chapters_list=ch_list_str,
            transcript=bounded_transcript
        )

        return self.provider.generate_content(
            system_prompt="You are a rapid AI summarization assistant specializing in fast, high-signal educational summaries.",
            user_prompt=prompt,
            temperature=0.2,
            max_tokens=2000
        )

    def generate_detailed_notes(
        self,
        title: str,
        duration_str: str,
        transcript_text: str,
        chapters: Optional[List[ChapterItem]] = None
    ) -> str:
        """
        Generates Option 2: Detailed Notes from transcript.
        Comprehensive study notes with overview, chapter-wise breakdown,
        definitions, examples, and synthesis.
        """
        logger.info(f"Generating Detailed Notes for video '{title}'")
        chapters_info = "No official chapters detected."
        if chapters and len(chapters) > 0:
            ch_lines = [f"- Chapter {i+1}: {c.title} [{c.timestamp_str or '00:00'}]" for i, c in enumerate(chapters)]
            chapters_info = "\n".join(ch_lines)

        # For detailed notes, preserve substantial transcript context
        bounded_transcript = transcript_text[:25000] if transcript_text else "No transcript text available."

        prompt = DETAILED_NOTES_PROMPT.format(
            title=title,
            duration=duration_str,
            chapters_info=chapters_info,
            transcript=bounded_transcript
        )

        return self.provider.generate_content(
            system_prompt="You are an expert pedagogical note-taker and technical author producing comprehensive academic notes.",
            user_prompt=prompt,
            temperature=0.25,
            max_tokens=4000
        )

