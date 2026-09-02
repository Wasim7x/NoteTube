import re
import yt_dlp
from app.models.schemas import VideoMetadata

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
    def get_video_metadata(url: str) -> VideoMetadata:
        """
        Fetches metadata for a YouTube video using yt-dlp.
        """
        video_id = YouTubeService.extract_video_id(url)
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return VideoMetadata(
                    id=video_id,
                    title=info.get('title', 'Unknown Title'),
                    thumbnail=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                )
        except Exception as e:
            # Fallback if yt-dlp fails (e.g. rate limit, changes)
            return VideoMetadata(
                id=video_id,
                title="YouTube Video",
                thumbnail=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            )

youtube_service = YouTubeService()
