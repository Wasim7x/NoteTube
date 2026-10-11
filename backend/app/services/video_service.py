import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.models.schemas import VideoMetadata, ChapterItem, LoadVideoResponse
from app.services.youtube_service import YouTubeService, youtube_service
from app.services.transcript_service import transcript_service
from app.services.chapter_service import chapter_service
from app.models.transcript import NormalizedTranscript

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
JOBS_DATA_DIR = _BACKEND_DIR / "data" / "jobs"
JOBS_DATA_DIR.mkdir(parents=True, exist_ok=True)

class VideoJobService:
    def __init__(self, data_dir: Path = JOBS_DATA_DIR):
        self.data_dir = data_dir.resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_job_path(self, video_id: str) -> Path:
        clean_id = YouTubeService.extract_video_id(video_id) if "http" in video_id else video_id
        clean_id = "".join(c for c in clean_id if c.isalnum() or c in "-_")[:64]
        return (self.data_dir / f"{clean_id}.json").resolve()

    def get_cached_job(self, video_id: str) -> Optional[Dict[str, Any]]:
        path = self.get_job_path(video_id)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read cached video job for {video_id}: {e}")
        return None

    def save_job(self, video_id: str, job_data: Dict[str, Any]) -> None:
        path = self.get_job_path(video_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save video job for {video_id}: {e}")

    def load_video(self, url: str) -> LoadVideoResponse:
        """
        Loads video metadata and extracts transcript once.
        Reuses cached job data if valid to avoid re-fetching yt-dlp and transcripts.
        """
        video_id = YouTubeService.extract_video_id(url)
        clean_url = f"https://www.youtube.com/watch?v={video_id}"

        # 1. Check existing job cache
        cached = self.get_cached_job(video_id)
        if cached:
            logger.info(f"Reusing cached video job for video_id={video_id}")
            return LoadVideoResponse(
                success=True,
                video_id=video_id,
                video=VideoMetadata(**cached["video"]),
                transcript_available=cached.get("transcript_available", False),
                transcript_language=cached.get("transcript_language"),
                transcript_language_code=cached.get("transcript_language_code"),
                transcript_generated=cached.get("transcript_generated"),
                transcript_preview=cached.get("transcript_preview"),
                transcript_char_count=cached.get("transcript_char_count", 0),
                has_chapters=cached.get("has_chapters", True),
                total_chapters=len(cached.get("chapters", [])),
                chapters=[ChapterItem(**c) for c in cached.get("chapters", [])]
            )

        # 2. Retrieve video metadata
        logger.info(f"Fetching fresh video metadata for video_id={video_id}")
        metadata = youtube_service.get_video_metadata(clean_url)

        # 3. Retrieve transcript
        logger.info(f"Fetching transcript for video_id={video_id}")
        transcript = transcript_service.get_transcript(video_id)

        transcript_str = str(transcript) if transcript is not None else ""
        transcript_available = bool(transcript and len(transcript_str.strip()) >= 50)

        transcript_lang = None
        transcript_lang_code = None
        transcript_gen = None
        transcript_preview = None
        transcript_char_count = 0
        raw_segments = []

        if transcript_available:
            if isinstance(transcript, NormalizedTranscript):
                transcript_lang = transcript.language
                transcript_lang_code = transcript.language_code
                transcript_gen = transcript.is_generated
                raw_segments = transcript.segments or []
            else:
                transcript_lang = getattr(transcript, "language", "English")
                transcript_lang_code = getattr(transcript, "language_code", "en")
                transcript_gen = getattr(transcript, "is_generated", False)
                raw_segments = getattr(transcript, "segments", [])

            transcript_char_count = len(transcript_str)
            transcript_preview = transcript_str[:250].strip() + ("..." if len(transcript_str) > 250 else "")

        # 4. Resolve chapters
        chapters: List[ChapterItem] = []
        if metadata.chapters and len(metadata.chapters) > 0:
            chapters = metadata.chapters
        elif transcript_available:
            # Fallback heuristic chapter partition when official chapters are absent
            heuristic_chapters = chapter_service._create_heuristic_chapters(
                segments=raw_segments,
                total_duration=float(metadata.duration or 300.0),
                target_count=min(8, max(3, int((metadata.duration or 300.0) // 180))),
                video_title=metadata.title
            )
            chapters = YouTubeService.normalize_chapters(heuristic_chapters, float(metadata.duration or 300.0))
            metadata.chapters = chapters

        # Standardize chapter IDs: ensure ch_1, ch_2...
        normalized_chapters: List[ChapterItem] = []
        for idx, ch in enumerate(chapters):
            ch_num = idx + 1
            normalized_chapters.append(ChapterItem(
                chapter_id=ch.chapter_id or f"ch_{ch_num}",
                title=ch.title,
                start_time=ch.start_time,
                end_time=ch.end_time,
                duration=ch.duration,
                timestamp_str=ch.timestamp_str or YouTubeService.format_timestamp(ch.start_time),
                duration_str=ch.duration_str,
                is_ai_detected=bool(ch.is_ai_detected),
                content=ch.content
            ))

        metadata.chapters = normalized_chapters

        # 5. Persist job in durable store
        job_record = {
            "video_id": video_id,
            "url": clean_url,
            "video": metadata.model_dump(),
            "transcript_available": transcript_available,
            "transcript_language": transcript_lang,
            "transcript_language_code": transcript_lang_code,
            "transcript_generated": transcript_gen,
            "transcript_preview": transcript_preview,
            "transcript_char_count": transcript_char_count,
            "transcript_full": transcript_str,
            "transcript_segments": raw_segments,
            "has_chapters": len(normalized_chapters) > 0,
            "chapters": [c.model_dump() for c in normalized_chapters]
        }
        self.save_job(video_id, job_record)

        return LoadVideoResponse(
            success=True,
            video_id=video_id,
            video=metadata,
            transcript_available=transcript_available,
            transcript_language=transcript_lang,
            transcript_language_code=transcript_lang_code,
            transcript_generated=transcript_gen,
            transcript_preview=transcript_preview,
            transcript_char_count=transcript_char_count,
            has_chapters=len(normalized_chapters) > 0,
            total_chapters=len(normalized_chapters),
            chapters=normalized_chapters
        )

video_job_service = VideoJobService()
