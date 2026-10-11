import logging
from typing import Generator, Dict, Any, Optional, List
from app.models.schemas import GenerateNotesResponse, NotesData, ChapterItem, VideoMetadata
from app.services.youtube_service import YouTubeService, youtube_service
from app.services.transcript_service import transcript_service
from app.services.summarization_service import SummarizationService
from app.services.chapter_service import chapter_service
from app.services.llm.factory import create_llm_provider
from app.models.transcript import NormalizedTranscript

logger = logging.getLogger(__name__)

class NotesService:
    @staticmethod
    def _extract_title(markdown_text: str, fallback_title: str) -> str:
        """Extracts title from markdown starting with # Title, else falls back to metadata."""
        if not markdown_text:
            return fallback_title
        for line in markdown_text.splitlines():
            s = line.strip()
            if s.startswith("# "):
                candidate = s[2:].strip()
                if candidate and not candidate.startswith("Chapter") and not candidate.startswith("Video Overview"):
                    return candidate
        return fallback_title

    def generate(self, url: str, provider: str, model: str, api_key: str) -> GenerateNotesResponse:
        """
        Synchronously generates comprehensive structured notes:
        1. Video Overview
        2. Chapter-by-Chapter Notes (chronologically, covering all chapters)
        3. Final Revision Section
        """
        try:
            # 1. Initialize LLM Provider with user configuration
            llm_provider = create_llm_provider(
                provider=provider,
                model=model,
                api_key=api_key
            )
            summarizer = SummarizationService(provider=llm_provider)

            # 2. Fetch YouTube metadata
            logger.info(f"Fetching metadata for {url}")
            metadata = youtube_service.get_video_metadata(url)

            # 3. Fetch transcript (language-agnostic, auto-discovering)
            logger.info(f"Fetching transcript for video {metadata.id}")
            transcript = transcript_service.get_transcript(metadata.id)

            transcript_str = str(transcript) if transcript is not None else ""
            has_valid_transcript = bool(transcript and len(transcript_str.strip()) >= 50)

            # Format total duration
            total_duration_sec = float(metadata.duration or 0.0)
            duration_str = YouTubeService.format_duration(total_duration_sec) if total_duration_sec > 0 else "N/A"

            if has_valid_transcript:
                fallback_used = False
                transcript_available = True
                if isinstance(transcript, NormalizedTranscript):
                    transcript_language = transcript.language
                    transcript_language_code = transcript.language_code
                    transcript_generated = transcript.is_generated
                else:
                    transcript_language = getattr(transcript, "language", "English")
                    transcript_language_code = getattr(transcript, "language_code", "en")
                    transcript_generated = getattr(transcript, "is_generated", False)

                logger.info(f"LLM Provider: {llm_provider.provider_name} | Model: {llm_provider.model_name}")
                logger.info(f"Transcript available ({len(transcript_str)} chars | language: {transcript_language})")

                # Detect / generate chapters
                chapters = chapter_service.detect_or_generate_chapters(
                    metadata=metadata,
                    transcript=transcript,
                    llm_provider=llm_provider
                )
                metadata.chapters = chapters

                # Associate transcript segments with chapters
                chapters_with_transcripts = chapter_service.associate_transcript_with_chapters(
                    chapters=chapters,
                    transcript=transcript
                )

                # A. Generate Video Overview
                logger.info("Generating Video Overview...")
                overview_context = f"Video Title: {metadata.title}\nDescription: {metadata.description or ''}\n\nKey Excerpt:\n{transcript_str[:3000]}"
                overview_content = summarizer.generate_video_overview(
                    title=metadata.title,
                    duration_str=duration_str,
                    context=overview_context
                )

                # B. Generate Chapter-by-Chapter Notes
                logger.info(f"Generating notes for {len(chapters)} chapters...")
                updated_chapters: List[ChapterItem] = []
                chapter_summaries_for_revision: List[str] = []

                for idx, (ch, ch_text) in enumerate(chapters_with_transcripts):
                    ch_num = idx + 1
                    logger.info(f"Generating chapter {ch_num}/{len(chapters)}: '{ch.title}' ({ch.timestamp_str})")
                    
                    ch_notes = summarizer.generate_chapter_notes(
                        chapter_num=ch_num,
                        chapter_title=ch.title,
                        timestamp_str=ch.timestamp_str or "00:00",
                        duration_str=ch.duration_str or "N/A",
                        transcript_text=ch_text
                    )
                    
                    ch_copy = ChapterItem(
                        chapter_id=ch.chapter_id or f"ch_{ch_num}",
                        title=ch.title,
                        start_time=ch.start_time,
                        end_time=ch.end_time,
                        duration=ch.duration,
                        timestamp_str=ch.timestamp_str,
                        duration_str=ch.duration_str,
                        is_ai_detected=ch.is_ai_detected,
                        content=ch_notes
                    )
                    updated_chapters.append(ch_copy)
                    chapter_summaries_for_revision.append(f"Chapter {ch_num}: {ch.title}\n{ch_notes[:1000]}")

                # C. Generate Final Revision Section
                logger.info("Generating Final Revision Section...")
                all_summaries_text = "\n\n---\n\n".join(chapter_summaries_for_revision)
                revision_content = summarizer.generate_final_revision(
                    title=metadata.title,
                    all_chapters_summary=all_summaries_text
                )

            else:
                # Fallback Pipeline when transcript is unavailable
                logger.info(f"Engaging fallback notes synthesis for video {metadata.id}")
                fallback_used = True
                transcript_available = False
                transcript_language = None
                transcript_language_code = None
                transcript_generated = None

                # Detect / generate chapters from metadata
                chapters = chapter_service.detect_or_generate_chapters(
                    metadata=metadata,
                    transcript=None,
                    llm_provider=llm_provider
                )
                metadata.chapters = chapters

                # A. Generate Video Overview from metadata & syllabus
                overview_context = (
                    f"Video Title: {metadata.title}\n"
                    f"Channel: {metadata.channel or 'Unknown'}\n"
                    f"Description: {metadata.description or 'No description provided.'}\n"
                    f"Chapters: {', '.join([c.title for c in chapters])}"
                )
                overview_content = summarizer.generate_video_overview(
                    title=metadata.title,
                    duration_str=duration_str,
                    context=overview_context
                )

                # B. Generate Chapter Notes from curriculum
                updated_chapters = []
                chapter_summaries_for_revision = []
                for idx, ch in enumerate(chapters):
                    ch_num = idx + 1
                    ch_context = f"Video: {metadata.title}\nDescription: {metadata.description or ''}"
                    ch_notes = summarizer.generate_fallback_chapter_notes(
                        chapter_num=ch_num,
                        chapter_title=ch.title,
                        timestamp_str=ch.timestamp_str or "00:00",
                        duration_str=ch.duration_str or "N/A",
                        context=ch_context
                    )
                    ch_copy = ChapterItem(
                        chapter_id=ch.chapter_id or f"ch_{ch_num}",
                        title=ch.title,
                        start_time=ch.start_time,
                        end_time=ch.end_time,
                        duration=ch.duration,
                        timestamp_str=ch.timestamp_str,
                        duration_str=ch.duration_str,
                        is_ai_detected=ch.is_ai_detected,
                        content=ch_notes
                    )
                    updated_chapters.append(ch_copy)
                    chapter_summaries_for_revision.append(f"Chapter {ch_num}: {ch.title}\n{ch_notes[:1000]}")

                # C. Generate Final Revision Section
                all_summaries_text = "\n\n---\n\n".join(chapter_summaries_for_revision)
                revision_content = summarizer.generate_final_revision(
                    title=metadata.title,
                    all_chapters_summary=all_summaries_text
                )

            # Build unified Markdown combining all sections
            full_markdown = summarizer.build_full_markdown(
                overview_content=overview_content,
                chapters=updated_chapters,
                revision_content=revision_content
            )

            notes_title = self._extract_title(full_markdown, metadata.title)
            notes_data = NotesData(
                title=notes_title,
                content=full_markdown
            )

            return GenerateNotesResponse(
                success=True,
                provider=llm_provider.provider_name,
                model=llm_provider.model_name,
                fallback_used=fallback_used,
                transcript_available=transcript_available,
                transcript_language=transcript_language,
                transcript_language_code=transcript_language_code,
                transcript_generated=transcript_generated,
                video=metadata,
                notes=notes_data,
                overview_content=overview_content,
                chapters=updated_chapters,
                revision_content=revision_content
            )

        except ValueError as ve:
            error_str = str(ve)
            logger.warning(f"Validation/Provider error: {error_str}")
            return GenerateNotesResponse(
                success=False,
                error=error_str
            )
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating notes: {error_str}")
            clean_error = error_str if ("youtube" in error_str.lower() or "transcript" in error_str.lower()) else f"Failed to generate notes: {error_str}"
            return GenerateNotesResponse(
                success=False,
                error=clean_error
            )

    def generate_stream(
        self,
        url: str,
        provider: str,
        model: str,
        api_key: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Yields progressive events during note generation for real-time frontend updates:
        - status: High-level status messages
        - metadata: Video info and detected chapters
        - overview: Generated Video Overview
        - chapter_start: When a chapter starts generating
        - chapter_complete: As each chapter note finishes
        - revision: Generated Final Revision Section
        - complete: Full final response object
        - error: On any failure
        """
        try:
            yield {"type": "status", "step": "init", "message": "Connecting to LLM and verifying configuration..."}
            
            llm_provider = create_llm_provider(
                provider=provider,
                model=model,
                api_key=api_key
            )
            summarizer = SummarizationService(provider=llm_provider)

            yield {"type": "status", "step": "metadata", "message": "Fetching video information and detecting chapters..."}
            metadata = youtube_service.get_video_metadata(url)

            yield {"type": "status", "step": "transcript", "message": "Retrieving transcript and detecting language..."}
            transcript = transcript_service.get_transcript(metadata.id)

            transcript_str = str(transcript) if transcript is not None else ""
            has_valid_transcript = bool(transcript and len(transcript_str.strip()) >= 50)

            total_duration_sec = float(metadata.duration or 0.0)
            duration_str = YouTubeService.format_duration(total_duration_sec) if total_duration_sec > 0 else "N/A"

            if has_valid_transcript:
                fallback_used = False
                transcript_available = True
                if isinstance(transcript, NormalizedTranscript):
                    transcript_language = transcript.language
                    transcript_language_code = transcript.language_code
                    transcript_generated = transcript.is_generated
                else:
                    transcript_language = getattr(transcript, "language", "English")
                    transcript_language_code = getattr(transcript, "language_code", "en")
                    transcript_generated = getattr(transcript, "is_generated", False)

                yield {"type": "status", "step": "chapters", "message": "Partitioning transcript by chapter timestamps..."}
                chapters = chapter_service.detect_or_generate_chapters(
                    metadata=metadata,
                    transcript=transcript,
                    llm_provider=llm_provider
                )
                metadata.chapters = chapters

                chapters_with_transcripts = chapter_service.associate_transcript_with_chapters(
                    chapters=chapters,
                    transcript=transcript
                )

                yield {
                    "type": "metadata",
                    "video": metadata.model_dump(),
                    "total_chapters": len(chapters),
                    "transcript_language": transcript_language,
                    "is_fallback": False
                }

                # A. Generate Video Overview
                yield {"type": "status", "step": "overview", "message": "Generating Video Overview..."}
                overview_context = f"Video Title: {metadata.title}\nDescription: {metadata.description or ''}\n\nKey Excerpt:\n{transcript_str[:3000]}"
                overview_content = summarizer.generate_video_overview(
                    title=metadata.title,
                    duration_str=duration_str,
                    context=overview_context
                )
                yield {"type": "overview", "overview_content": overview_content}

                # B. Generate Chapter Notes progressively
                updated_chapters: List[ChapterItem] = []
                chapter_summaries_for_revision: List[str] = []
                total_ch = len(chapters_with_transcripts)

                for idx, (ch, ch_text) in enumerate(chapters_with_transcripts):
                    ch_num = idx + 1
                    msg = f"Generating Chapter {ch_num} of {total_ch}: {ch.title}"
                    yield {
                        "type": "chapter_start",
                        "index": idx,
                        "chapter_num": ch_num,
                        "total": total_ch,
                        "title": ch.title,
                        "timestamp_str": ch.timestamp_str,
                        "message": msg
                    }

                    ch_notes = summarizer.generate_chapter_notes(
                        chapter_num=ch_num,
                        chapter_title=ch.title,
                        timestamp_str=ch.timestamp_str or "00:00",
                        duration_str=ch.duration_str or "N/A",
                        transcript_text=ch_text
                    )

                    ch_item = ChapterItem(
                        chapter_id=ch.chapter_id or f"ch_{ch_num}",
                        title=ch.title,
                        start_time=ch.start_time,
                        end_time=ch.end_time,
                        duration=ch.duration,
                        timestamp_str=ch.timestamp_str,
                        duration_str=ch.duration_str,
                        is_ai_detected=ch.is_ai_detected,
                        content=ch_notes
                    )
                    updated_chapters.append(ch_item)
                    chapter_summaries_for_revision.append(f"Chapter {ch_num}: {ch.title}\n{ch_notes[:1000]}")

                    yield {
                        "type": "chapter_complete",
                        "index": idx,
                        "chapter_num": ch_num,
                        "total": total_ch,
                        "chapter": ch_item.model_dump()
                    }

                # C. Generate Final Revision Section
                yield {"type": "status", "step": "revision", "message": "Finalizing revision notes & self-assessment..."}
                all_summaries_text = "\n\n---\n\n".join(chapter_summaries_for_revision)
                revision_content = summarizer.generate_final_revision(
                    title=metadata.title,
                    all_chapters_summary=all_summaries_text
                )
                yield {"type": "revision", "revision_content": revision_content}

            else:
                # Fallback stream
                fallback_used = True
                transcript_available = False
                transcript_language = None
                transcript_language_code = None
                transcript_generated = None

                yield {"type": "status", "step": "fallback", "message": "Synthesizing notes from curriculum & chapters (captions unavailable)..."}
                chapters = chapter_service.detect_or_generate_chapters(
                    metadata=metadata,
                    transcript=None,
                    llm_provider=llm_provider
                )
                metadata.chapters = chapters

                yield {
                    "type": "metadata",
                    "video": metadata.model_dump(),
                    "total_chapters": len(chapters),
                    "is_fallback": True
                }

                # Overview
                yield {"type": "status", "step": "overview", "message": "Generating Video Overview..."}
                overview_context = (
                    f"Video Title: {metadata.title}\n"
                    f"Channel: {metadata.channel or 'Unknown'}\n"
                    f"Description: {metadata.description or 'No description provided.'}\n"
                    f"Chapters: {', '.join([c.title for c in chapters])}"
                )
                overview_content = summarizer.generate_video_overview(
                    title=metadata.title,
                    duration_str=duration_str,
                    context=overview_context
                )
                yield {"type": "overview", "overview_content": overview_content}

                # Chapters
                updated_chapters = []
                chapter_summaries_for_revision = []
                total_ch = len(chapters)

                for idx, ch in enumerate(chapters):
                    ch_num = idx + 1
                    msg = f"Generating Chapter {ch_num} of {total_ch}: {ch.title}"
                    yield {
                        "type": "chapter_start",
                        "index": idx,
                        "chapter_num": ch_num,
                        "total": total_ch,
                        "title": ch.title,
                        "timestamp_str": ch.timestamp_str,
                        "message": msg
                    }

                    ch_context = f"Video: {metadata.title}\nDescription: {metadata.description or ''}"
                    ch_notes = summarizer.generate_fallback_chapter_notes(
                        chapter_num=ch_num,
                        chapter_title=ch.title,
                        timestamp_str=ch.timestamp_str or "00:00",
                        duration_str=ch.duration_str or "N/A",
                        context=ch_context
                    )
                    ch_item = ChapterItem(
                        chapter_id=ch.chapter_id or f"ch_{ch_num}",
                        title=ch.title,
                        start_time=ch.start_time,
                        end_time=ch.end_time,
                        duration=ch.duration,
                        timestamp_str=ch.timestamp_str,
                        duration_str=ch.duration_str,
                        is_ai_detected=ch.is_ai_detected,
                        content=ch_notes
                    )
                    updated_chapters.append(ch_item)
                    chapter_summaries_for_revision.append(f"Chapter {ch_num}: {ch.title}\n{ch_notes[:1000]}")

                    yield {
                        "type": "chapter_complete",
                        "index": idx,
                        "chapter_num": ch_num,
                        "total": total_ch,
                        "chapter": ch_item.model_dump()
                    }

                # Revision
                yield {"type": "status", "step": "revision", "message": "Finalizing revision notes & self-assessment..."}
                all_summaries_text = "\n\n---\n\n".join(chapter_summaries_for_revision)
                revision_content = summarizer.generate_final_revision(
                    title=metadata.title,
                    all_chapters_summary=all_summaries_text
                )
                yield {"type": "revision", "revision_content": revision_content}

            # Finalize unified response
            full_markdown = summarizer.build_full_markdown(
                overview_content=overview_content,
                chapters=updated_chapters,
                revision_content=revision_content
            )
            notes_title = self._extract_title(full_markdown, metadata.title)
            notes_data = NotesData(
                title=notes_title,
                content=full_markdown
            )

            final_response = GenerateNotesResponse(
                success=True,
                provider=llm_provider.provider_name,
                model=llm_provider.model_name,
                fallback_used=fallback_used,
                transcript_available=transcript_available,
                transcript_language=transcript_language,
                transcript_language_code=transcript_language_code,
                transcript_generated=transcript_generated,
                video=metadata,
                notes=notes_data,
                overview_content=overview_content,
                chapters=updated_chapters,
                revision_content=revision_content
            )

            yield {
                "type": "complete",
                "response": final_response.model_dump()
            }

        except Exception as e:
            error_str = str(e)
            logger.error(f"Streaming generation error: {error_str}")
            clean_error = error_str if ("youtube" in error_str.lower() or "transcript" in error_str.lower()) else f"Failed to generate notes: {error_str}"
            yield {
                "type": "error",
                "error": clean_error
            }

notes_service = NotesService()
