import json
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import VideoMetadata, ChapterItem
from app.models.transcript import NormalizedTranscript
from app.services.chapter_service import chapter_service
from app.services.notes_service import notes_service
from app.services.youtube_service import YouTubeService
from app.services.llm.base import LLMProvider

class TestAllRequiredScenarios(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.ollama.OllamaProvider.generate_content")
    def test_scenario_1_video_with_youtube_chapters(self, mock_gen, mock_transcript, mock_meta):
        """Scenario 1: A video with official YouTube chapters."""
        mock_meta.return_value = VideoMetadata(
            id="vid_ch_official",
            title="Docker and Containers Full Course",
            thumbnail="https://example.com/thumb.jpg",
            duration=1200,
            chapters=[
                ChapterItem(title="Introduction to Docker", start_time=0.0, end_time=300.0, is_ai_detected=False),
                ChapterItem(title="Docker Architecture & Images", start_time=300.0, end_time=700.0, is_ai_detected=False),
                ChapterItem(title="Docker Compose & Multi-Container", start_time=700.0, end_time=1200.0, is_ai_detected=False)
            ]
        )
        mock_transcript.return_value = NormalizedTranscript(
            text="Welcome to Docker. Docker uses images and daemon. Docker Compose orchestrates containers.",
            language="English",
            language_code="en",
            is_generated=False,
            segments=[
                {"start": 10.0, "duration": 5.0, "text": "Welcome to Docker."},
                {"start": 350.0, "duration": 10.0, "text": "Docker uses images and daemon."},
                {"start": 750.0, "duration": 15.0, "text": "Docker Compose orchestrates containers."}
            ]
        )
        mock_gen.side_effect = [
            "# Docker Full Course\n\n## Video Overview\nComprehensive introduction to Docker containers and architecture.",
            "## Chapter 1: Introduction to Docker\n**Timestamp:** 00:00 – 05:00\n**Duration:** 5 minutes\n\n### 1. Chapter Summary\nClear explanation of Docker.",
            "## Chapter 2: Docker Architecture & Images\n**Timestamp:** 05:00 – 11:40\n**Duration:** 6 minutes 40 seconds\n\n### 1. Chapter Summary\nImages details.",
            "## Chapter 3: Docker Compose & Multi-Container\n**Timestamp:** 11:40 – 20:00\n**Duration:** 8 minutes 20 seconds\n\n### 1. Chapter Summary\nCompose orchestration.",
            "## Final Revision\n### 1. Complete Video Summary\nDocker simplifies development."
        ]

        resp = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_ch_official",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )

        self.assertTrue(resp.success)
        self.assertFalse(resp.fallback_used)
        self.assertEqual(len(resp.chapters), 3)
        # Verify official chapters are NOT marked as AI-detected
        self.assertFalse(resp.chapters[0].is_ai_detected)
        self.assertFalse(resp.chapters[1].is_ai_detected)
        self.assertFalse(resp.chapters[2].is_ai_detected)
        self.assertEqual(resp.chapters[0].title, "Introduction to Docker")
        self.assertIn("## Video Overview", resp.notes.content)
        self.assertIn("## Chapter 1: Introduction to Docker", resp.notes.content)
        self.assertIn("## Final Revision", resp.notes.content)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.ollama.OllamaProvider.generate_content")
    def test_scenario_2_video_without_official_chapters(self, mock_gen, mock_transcript, mock_meta):
        """Scenario 2: A video without official chapters -> creates AI-detected chapters labeled is_ai_detected=True."""
        mock_meta.return_value = VideoMetadata(
            id="vid_no_chapters",
            title="Git Branching Strategies",
            thumbnail="https://example.com/thumb.jpg",
            duration=600,
            chapters=None
        )
        segments = [
            {"start": float(s), "duration": 20.0, "text": f"Git workflow segment at {s}s"}
            for s in range(0, 600, 30)
        ]
        mock_transcript.return_value = NormalizedTranscript(
            text="Git workflow explanation. " * 20,
            language="English",
            language_code="en",
            is_generated=True,
            segments=segments
        )
        mock_gen.return_value = "## Chapter Notes\n### 1. Summary\nGit concepts."

        resp = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_no_chapters",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )

        self.assertTrue(resp.success)
        self.assertTrue(len(resp.chapters) >= 2)
        # Verify all detected chapters are marked as AI-detected
        for ch in resp.chapters:
            self.assertTrue(ch.is_ai_detected, f"Chapter {ch.title} should be marked is_ai_detected=True")
            self.assertIsNotNone(ch.timestamp_str)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.ollama.OllamaProvider.generate_content")
    def test_scenario_3_long_video_many_chapters(self, mock_gen, mock_transcript, mock_meta):
        """Scenario 3: A long video containing many chapters (e.g. 8 chapters)."""
        chapters = []
        for i in range(8):
            start = i * 600.0
            end = (i + 1) * 600.0
            chapters.append(ChapterItem(
                title=f"Module {i+1}: Advanced Topic {i+1}",
                start_time=start,
                end_time=end,
                is_ai_detected=False
            ))

        mock_meta.return_value = VideoMetadata(
            id="vid_long_8ch",
            title="Complete 8-Hour Full Stack Bootcamp",
            thumbnail="https://example.com/thumb.jpg",
            duration=4800,
            chapters=chapters
        )
        segments = []
        for i in range(8):
            segments.append({
                "start": i * 600.0 + 10.0,
                "duration": 50.0,
                "text": f"This is detailed content for module {i+1} covering architecture."
            })
        mock_transcript.return_value = NormalizedTranscript(
            text="Full stack bootcamp covering frontend, backend, databases, and DevOps.",
            language="English",
            language_code="en",
            is_generated=False,
            segments=segments
        )
        mock_gen.return_value = "## Structured Section\n### 1. Summary\nHigh-density content."

        resp = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_long_8ch",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )

        self.assertTrue(resp.success)
        self.assertEqual(len(resp.chapters), 8)
        self.assertEqual(resp.chapters[7].title, "Module 8: Advanced Topic 8")
        self.assertIsNotNone(resp.notes.content)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.ollama.OllamaProvider.generate_content")
    def test_scenario_4_transcript_in_language_other_than_english(self, mock_gen, mock_transcript, mock_meta):
        """Scenario 4: A transcript in a language other than English (e.g., Hindi or Spanish)."""
        mock_meta.return_value = VideoMetadata(
            id="vid_hindi",
            title="Machine Learning in Hindi",
            thumbnail="https://example.com/thumb.jpg",
            duration=600,
            chapters=[
                ChapterItem(title="ML Parichay", start_time=0.0, end_time=300.0, is_ai_detected=False),
                ChapterItem(title="Supervised Learning", start_time=300.0, end_time=600.0, is_ai_detected=False)
            ]
        )
        mock_transcript.return_value = NormalizedTranscript(
            text="Namaste dosto, aaj hum Machine Learning ke baare mein baat karenge. Supervised learning algorithms.",
            language="Hindi",
            language_code="hi",
            is_generated=False,
            segments=[
                {"start": 5.0, "duration": 10.0, "text": "Namaste dosto, aaj hum Machine Learning ke baare mein baat karenge."},
                {"start": 310.0, "duration": 10.0, "text": "Supervised learning algorithms regression aur classification karte hain."}
            ]
        )
        mock_gen.return_value = "## Overview\nCovers machine learning fundamentals in English."

        resp = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_hindi",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )

        self.assertTrue(resp.success)
        self.assertEqual(resp.transcript_language, "Hindi")
        self.assertEqual(resp.transcript_language_code, "hi")
        self.assertFalse(resp.fallback_used)
        self.assertTrue(resp.transcript_available)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.ollama.OllamaProvider.generate_content")
    def test_scenario_5_video_with_missing_transcript(self, mock_gen, mock_transcript, mock_meta):
        """Scenario 5: A video with missing or unavailable transcript -> fallback synthesis."""
        mock_meta.return_value = VideoMetadata(
            id="vid_missing_trans",
            title="Quantum Computing Roadmap",
            thumbnail="https://example.com/thumb.jpg",
            duration=1200,
            description="Comprehensive syllabus covering qubits, superposition, and quantum gates.",
            chapters=[
                ChapterItem(title="Qubits & Superposition", start_time=0.0, end_time=600.0, is_ai_detected=False),
                ChapterItem(title="Quantum Algorithms", start_time=600.0, end_time=1200.0, is_ai_detected=False)
            ]
        )
        mock_transcript.return_value = None  # No transcript available
        mock_gen.return_value = "## Quantum Computing Notes\nSynthesized from syllabus."

        resp = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_missing_trans",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )

        self.assertTrue(resp.success)
        self.assertTrue(resp.fallback_used)
        self.assertFalse(resp.transcript_available)
        self.assertIsNone(resp.transcript_language)
        self.assertEqual(len(resp.chapters), 2)
        self.assertIn("Quantum Computing Notes", resp.notes.content)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.ollama.OllamaProvider.generate_content")
    def test_scenario_6_failed_ollama_request_and_retry(self, mock_gen, mock_transcript, mock_meta):
        """Scenario 6: Failed Ollama request (timeout/connection) returns error, then subsequent retry succeeds."""
        mock_meta.return_value = VideoMetadata(
            id="vid_retry_test",
            title="FastAPI Microservices",
            thumbnail="https://example.com/thumb.jpg",
            duration=300
        )
        mock_transcript.return_value = NormalizedTranscript(
            text="FastAPI is a modern web framework for Python.",
            language="English",
            language_code="en",
            is_generated=False,
            segments=[{"start": 0.0, "duration": 5.0, "text": "FastAPI is a modern web framework for Python."}]
        )

        # First call fails (e.g. Ollama service temporarily loading)
        mock_gen.side_effect = ValueError("Could not connect to Ollama service at http://localhost:11434.")
        resp1 = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_retry_test",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )
        self.assertFalse(resp1.success)
        self.assertIn("Could not connect to Ollama", resp1.error)

        # Retry succeeds
        mock_gen.side_effect = None
        mock_gen.return_value = "# FastAPI Microservices\n\n## Overview\nHigh performance APIs."
        resp2 = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_retry_test",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )
        self.assertTrue(resp2.success)
        self.assertIn("FastAPI Microservices", resp2.notes.title)

    def test_scenario_8_clicking_chapter_timestamps_navigation(self):
        """Scenario 8: Chapter timestamps format and URL generation maps precisely to YouTube position."""
        video_id = "dQw4w9WgXcQ"
        test_cases = [
            (0.0, "00:00", f"https://www.youtube.com/watch?v={video_id}&t=0s"),
            (125.0, "02:05", f"https://www.youtube.com/watch?v={video_id}&t=125s"),
            (3665.0, "01:01:05", f"https://www.youtube.com/watch?v={video_id}&t=3665s"),
        ]

        for seconds, expected_formatted, expected_url in test_cases:
            formatted = YouTubeService.format_timestamp(seconds)
            self.assertEqual(formatted, expected_formatted)
            generated_url = f"https://www.youtube.com/watch?v={video_id}&t={int(seconds)}s"
            self.assertEqual(generated_url, expected_url)

if __name__ == "__main__":
    unittest.main()
