from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "start": self.start,
            "duration": self.duration
        }

@dataclass
class NormalizedTranscript:
    text: str
    language: str
    language_code: str
    is_generated: bool
    source: str = "youtube"
    segments: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "language": self.language,
            "language_code": self.language_code,
            "is_generated": self.is_generated,
            "source": self.source,
            "segments": self.segments
        }

    def __str__(self) -> str:
        return self.text

    def __len__(self) -> int:
        return len(self.text)

    def strip(self, *args, **kwargs) -> str:
        return self.text.strip(*args, **kwargs)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def __bool__(self) -> bool:
        return bool(self.text and self.text.strip())
