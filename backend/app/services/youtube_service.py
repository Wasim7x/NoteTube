import re
from typing import List, Optional
import yt_dlp
from app.models.schemas import VideoMetadata, ChapterItem

class YouTubeService:
    @staticmethod
    def extract_video_id(url: str) -> str:
        """
        Extracts the YouTube video ID from a given URL.
        Supports standard and shortened URLs.
        """
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        raise ValueError("Invalid YouTube URL")

    @staticmethod
    def format_timestamp(seconds: Optional[float]) -> str:
        if seconds is None:
            return "00:00"
        s = max(0, int(seconds))
        hours = s // 3600
        minutes = (s % 3600) // 60
        secs = s % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_duration(seconds: Optional[float]) -> str:
        if seconds is None or seconds <= 0:
            return "0 seconds"
        s = max(0, int(seconds))
        hours = s // 3600
        minutes = (s % 3600) // 60
        secs = s % 60
        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if secs > 0 or not parts:
            parts.append(f"{secs} second{'s' if secs != 1 else ''}")
        return " ".join(parts)

    @staticmethod
    def _parse_chapters_from_description(description: str) -> List[ChapterItem]:
        """
        Parses timestamps and chapter titles commonly found in video descriptions.
        Matches lines like: 01:23 Introduction or 1:05:30 Core Architecture
        """
        chapters = []
        if not description:
            return chapters

        pattern = re.compile(r'(?:^|\n)\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—:]?\s*(.+)', re.MULTILINE)
        for match in pattern.finditer(description):
            timestamp_str, raw_title = match.groups()
            title = raw_title.strip()
            parts = [int(p) for p in timestamp_str.split(':')]
            if len(parts) == 2:
                seconds = parts[0] * 60 + parts[1]
            elif len(parts) == 3:
                seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
            else:
                continue
            chapters.append(ChapterItem(
                title=title,
                start_time=float(seconds),
                is_ai_detected=False
            ))
        return chapters

    @staticmethod
    def normalize_chapters(chapters: List[ChapterItem], total_duration: Optional[float] = None) -> List[ChapterItem]:
        """
        Ensures chapters are chronologically sorted and each has valid end_time, duration,
        timestamp_str, and duration_str.
        """
        if not chapters:
            return []

        sorted_chapters = sorted(chapters, key=lambda c: c.start_time)
        normalized: List[ChapterItem] = []
        count = len(sorted_chapters)

        for i, ch in enumerate(sorted_chapters):
            start = max(0.0, ch.start_time)
            if ch.end_time is not None and ch.end_time > start:
                end = ch.end_time
            elif i + 1 < count:
                end = sorted_chapters[i + 1].start_time
            elif total_duration and total_duration > start:
                end = float(total_duration)
            else:
                end = start + 180.0  # reasonable fallback if unknown

            dur = max(0.0, end - start)
            start_str = YouTubeService.format_timestamp(start)
            end_str = YouTubeService.format_timestamp(end)
            dur_str = YouTubeService.format_duration(dur)

            normalized.append(ChapterItem(
                chapter_id=ch.chapter_id or f"ch_{i + 1}",
                title=ch.title,
                start_time=start,
                end_time=end,
                duration=dur,
                timestamp_str=f"{start_str} – {end_str}",
                duration_str=dur_str,
                is_ai_detected=bool(ch.is_ai_detected),
                content=ch.content
            ))

        return normalized

    @staticmethod
    def get_video_metadata(url: str) -> VideoMetadata:
        """
        Fetches metadata for a YouTube video using yt-dlp including chapters,
        description, duration, and channel for downstream synthesis and fallback.
        """
        video_id = YouTubeService.extract_video_id(url)
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'extract_flat': True,
            'noplaylist': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                
                # Extract chapters from yt-dlp or fallback to description timestamps
                raw_chapters = info.get('chapters') or []
                chapters: List[ChapterItem] = []
                for ch in raw_chapters:
                    chapters.append(ChapterItem(
                        title=ch.get('title', 'Untitled Chapter'),
                        start_time=float(ch.get('start_time', 0.0)),
                        end_time=float(ch.get('end_time', 0.0)) if ch.get('end_time') is not None else None,
                        is_ai_detected=False
                    ))

                description = info.get('description') or ''
                if not chapters and description:
                    chapters = YouTubeService._parse_chapters_from_description(description)

                duration_val = info.get('duration')
                if chapters:
                    chapters = YouTubeService.normalize_chapters(chapters, float(duration_val) if duration_val else None)

                return VideoMetadata(
                    id=video_id,
                    title=info.get('title', 'Unknown Title'),
                    thumbnail=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                    description=description,
                    duration=duration_val,
                    chapters=chapters if chapters else None,
                    channel=info.get('channel') or info.get('uploader')
                )
        except Exception:
            # Fallback if yt-dlp fails (e.g. rate limit, changes)
            return VideoMetadata(
                id=video_id,
                title="YouTube Video",
                thumbnail=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            )

youtube_service = YouTubeService()
