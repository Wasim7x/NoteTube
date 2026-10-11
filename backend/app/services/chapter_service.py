import json
import logging
import re
from typing import List, Tuple, Optional, Any
from app.models.schemas import VideoMetadata, ChapterItem
from app.models.transcript import NormalizedTranscript
from app.services.youtube_service import YouTubeService
from app.prompts.notes_prompt import DETECT_CHAPTERS_PROMPT
from app.utils.text_processing import clean_text

logger = logging.getLogger(__name__)

class ChapterService:
    @staticmethod
    def _clean_json_response(raw_text: str) -> str:
        """Strips markdown code blocks and excess whitespace to extract JSON string."""
        cleaned = raw_text.strip()
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
        if match:
            return match.group(1).strip()
        start = cleaned.find('[')
        end = cleaned.rfind(']')
        if start != -1 and end != -1 and end > start:
            return cleaned[start:end+1]
        return cleaned

    @classmethod
    def _extract_segments(cls, transcript: Any, default_target_count: int = 3) -> List[Dict[str, Any]]:
        """Safely extracts segment dicts whether transcript is NormalizedTranscript, dict, or raw str."""
        if hasattr(transcript, "segments") and getattr(transcript, "segments"):
            return getattr(transcript, "segments")
        if isinstance(transcript, dict) and "segments" in transcript:
            return transcript["segments"]
        if isinstance(transcript, str) and transcript.strip():
            words = transcript.split()
            chunk_word_count = max(10, len(words) // max(1, default_target_count))
            synthesized = []
            for idx, i in enumerate(range(0, len(words), chunk_word_count)):
                chunk_words = words[i:i + chunk_word_count]
                synthesized.append({
                    "start": float(idx * 60.0),
                    "duration": 60.0,
                    "text": " ".join(chunk_words)
                })
            return synthesized
        return []

    @staticmethod
    def _create_heuristic_chapters(
        segments: List[Any],
        total_duration: float,
        target_count: int,
        video_title: str
    ) -> List[ChapterItem]:
        """
        Intelligently divides segments into logical topic-based chapters using
        time slices and natural speech pauses when LLM is unavailable or unneeded.
        """
        if not segments or target_count <= 1:
            dur = max(60.0, total_duration)
            return [
                ChapterItem(
                    title=f"Overview: {video_title[:50]}",
                    start_time=0.0,
                    end_time=dur,
                    is_ai_detected=True
                )
            ]

        interval = total_duration / target_count
        chapters: List[ChapterItem] = []
        
        title_templates = [
            "Introduction & Overview",
            "Core Concepts & Fundamentals",
            "Detailed Analysis & Implementation",
            "Workflows, Methods & Deep Dive",
            "Practical Demonstrations & Examples",
            "Advanced Techniques & Edge Cases",
            "Review, Best Practices & Summary",
            "Conclusion & Final Takeaways"
        ]

        for i in range(target_count):
            ideal_start = i * interval
            if i == 0:
                actual_start = 0.0
            else:
                closest_seg = min(segments, key=lambda s: abs(float(s.get("start", 0.0)) - ideal_start))
                actual_start = float(closest_seg.get("start", ideal_start))

            if i < len(title_templates):
                base_title = title_templates[i]
            else:
                base_title = f"Topic Section {i + 1}"

            seg_at_start = [s for s in segments if float(s.get("start", 0.0)) >= actual_start]
            if seg_at_start:
                first_snippet = seg_at_start[0].get("text", "").strip()
                if len(first_snippet) > 10 and not any(filler in first_snippet.lower() for filler in ["hello", "welcome", "subscribe", "today we"]):
                    words = [w.strip(".,;:?!") for w in first_snippet.split() if len(w) > 3]
                    if len(words) >= 3:
                        enriched = " ".join(words[:4]).title()
                        base_title = f"{base_title}: {enriched}"

            chapters.append(ChapterItem(
                title=base_title,
                start_time=actual_start,
                is_ai_detected=True
            ))

        return chapters

    @classmethod
    def detect_or_generate_chapters(
        cls,
        metadata: VideoMetadata,
        transcript: Optional[Any],
        llm_provider: Optional[Any] = None
    ) -> List[ChapterItem]:
        """
        Identifies official YouTube chapters or intelligently divides transcript
        into logical topic-based chapters labeled as AI-detected chapters.
        """
        # Case 1: Official chapters exist from yt-dlp or video description
        if metadata.chapters and len(metadata.chapters) > 0:
            logger.info(f"Using {len(metadata.chapters)} official YouTube chapters from video metadata.")
            sorted_ch = sorted(metadata.chapters, key=lambda c: c.start_time)
            if sorted_ch[0].start_time > 15.0:
                intro = ChapterItem(
                    title="Introduction",
                    start_time=0.0,
                    end_time=sorted_ch[0].start_time,
                    is_ai_detected=False
                )
                sorted_ch.insert(0, intro)
            
            for ch in sorted_ch:
                ch.is_ai_detected = False
            return YouTubeService.normalize_chapters(sorted_ch, metadata.duration)

        # Case 2: Official chapters unavailable -> Intelligently generate AI-detected chapters
        logger.info(f"Official chapters unavailable for video {metadata.id}. Performing AI topic chapter segmentation.")
        
        segments = cls._extract_segments(transcript)
        total_duration = float(metadata.duration or 0.0)
        if segments and (total_duration <= 0.0 or segments[-1].get("start", 0.0) > total_duration):
            last_seg = segments[-1]
            total_duration = float(last_seg.get("start", 0.0)) + float(last_seg.get("duration", 0.0))

        if total_duration <= 0.0:
            total_duration = 300.0

        if total_duration <= 180.0:
            target_count = 2
        elif total_duration <= 600.0:
            target_count = 3
        elif total_duration <= 1500.0:
            target_count = 4
        elif total_duration <= 3000.0:
            target_count = 6
        else:
            target_count = min(10, max(5, int(total_duration / 400.0)))

        # Try LLM-based intelligent chapter detection for cloud LLMs, use instant topic segmentation for local Ollama
        if llm_provider is not None and getattr(llm_provider, "provider_name", "") != "ollama" and segments and len(segments) >= 2:
            try:
                step = max(1, len(segments) // 20)
                sampled_lines = []
                for idx in range(0, len(segments), step):
                    seg = segments[idx]
                    t_str = YouTubeService.format_timestamp(float(seg.get("start", 0.0)))
                    text_snippet = seg.get("text", "")[:75].strip()
                    sampled_lines.append(f"[{t_str}] {text_snippet}")

                outline_text = "\n".join(sampled_lines[:25])
                prompt = DETECT_CHAPTERS_PROMPT.format(
                    title=metadata.title,
                    target_count=target_count,
                    transcript_outline=outline_text
                )

                logger.info(f"Requesting AI chapter segmentation from {llm_provider.provider_name}...")
                raw_output = llm_provider.generate_content(
                    system_prompt="You are an expert video content analyzer and technical curriculum designer.",
                    user_prompt=prompt,
                    temperature=0.1,
                    max_tokens=1000
                )

                cleaned_json = cls._clean_json_response(raw_output)
                parsed = json.loads(cleaned_json)

                if isinstance(parsed, list) and len(parsed) >= 2:
                    ai_chapters: List[ChapterItem] = []
                    for item in parsed:
                        if isinstance(item, dict) and "title" in item and "start_time" in item:
                            st = float(item["start_time"])
                            ai_chapters.append(ChapterItem(
                                title=str(item["title"]).strip(),
                                start_time=st,
                                is_ai_detected=True
                            ))

                    ai_chapters = sorted(ai_chapters, key=lambda c: c.start_time)
                    if ai_chapters[0].start_time > 0.0:
                        ai_chapters[0].start_time = 0.0

                    normalized = YouTubeService.normalize_chapters(ai_chapters, total_duration)
                    logger.info(f"AI chapter detection succeeded: generated {len(normalized)} chapters.")
                    return normalized

            except Exception as e:
                logger.warning(f"LLM chapter detection failed or timed out ({e}). Falling back to heuristic segmentation.")

        heuristic_ch = cls._create_heuristic_chapters(
            segments=segments,
            total_duration=total_duration,
            target_count=target_count,
            video_title=metadata.title
        )
        return YouTubeService.normalize_chapters(heuristic_ch, total_duration)

    @classmethod
    def associate_transcript_with_chapters(
        cls,
        chapters: List[ChapterItem],
        transcript: Optional[Any]
    ) -> List[Tuple[ChapterItem, str]]:
        """
        Associates transcript segments with the correct chapter using timestamps.
        Prevents mixing information from different chapters.
        """
        if not chapters:
            return []

        if not transcript:
            return [(ch, "") for ch in chapters]

        # If transcript is a plain string without segment breakdown
        if isinstance(transcript, str) and not hasattr(transcript, "segments"):
            words = transcript.split()
            if not words:
                return [(ch, "") for ch in chapters]
            chunk_size = max(1, len(words) // len(chapters))
            result: List[Tuple[ChapterItem, str]] = []
            for i, ch in enumerate(chapters):
                start_w = i * chunk_size
                end_w = (i + 1) * chunk_size if i < len(chapters) - 1 else len(words)
                part = " ".join(words[start_w:end_w])
                result.append((ch, clean_text(part)))
            return result

        segments = cls._extract_segments(transcript, default_target_count=len(chapters))
        if not segments:
            return [(ch, "") for ch in chapters]

        result = []
        num_chapters = len(chapters)

        for i, chapter in enumerate(chapters):
            start = chapter.start_time
            end = chapter.end_time if chapter.end_time is not None else (start + 999999.0)
            is_last = (i == num_chapters - 1)

            chapter_segments = []
            for seg in segments:
                seg_start = float(seg.get("start", 0.0))
                if is_last:
                    if seg_start >= start:
                        chapter_segments.append(seg.get("text", ""))
                else:
                    if start <= seg_start < end:
                        chapter_segments.append(seg.get("text", ""))

            raw_text = " ".join(chapter_segments)
            cleaned = clean_text(raw_text)
            result.append((chapter, cleaned))

        return result

chapter_service = ChapterService()
