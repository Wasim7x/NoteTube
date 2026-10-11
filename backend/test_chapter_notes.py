import json
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import VideoMetadata, ChapterItem
from app.models.transcript import NormalizedTranscript
from app.services.chapter_service import chapter_service
from app.services.notes_service import notes_service
from app.services.summarization_service import SummarizationService
from app.services.llm.base import LLMProvider

class TestChapterNotesSystem(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_official_chapters_used_and_normalized(self):
        """Scenario 1: Official YouTube chapters provided -> used chronologically with is_ai_detected=False."""
        metadata = VideoMetadata(
            id="vid_official",
            title="Python Masterclass",
            thumbnail="https://example.com/thumb.jpg",
            duration=600,
            chapters=[
                ChapterItem(title="Setup & Installation", start_time=0.0, is_ai_detected=False),
                ChapterItem(title="Variables & Types", start_time=180.0, is_ai_detected=False),
                ChapterItem(title="Functions & Modules", start_time=420.0, is_ai_detected=False)
            ]
        )
        transcript = NormalizedTranscript(
            text="Welcome to Python. Let's do setup. Now variables. Now functions.",
            language="English",
            language_code="en",
            is_generated=False,
            segments=[
                {"start": 10.0, "duration": 5.0, "text": "Welcome to Python."},
                {"start": 200.0, "duration": 10.0, "text": "Variables in Python store data."},
                {"start": 450.0, "duration": 15.0, "text": "Functions define reusable code."}
            ]
        )

        detected = chapter_service.detect_or_generate_chapters(metadata, transcript)
        self.assertEqual(len(detected), 3)
        self.assertFalse(detected[0].is_ai_detected)
        self.assertEqual(detected[0].title, "Setup & Installation")
        self.assertEqual(detected[0].start_time, 0.0)
        self.assertEqual(detected[0].end_time, 180.0)
        self.assertEqual(detected[0].timestamp_str, "00:00 – 03:00")
        self.assertIn("3 minute", detected[0].duration_str)

        # Verify timestamp segment association prevents mixing
        associated = chapter_service.associate_transcript_with_chapters(detected, transcript)
        self.assertEqual(len(associated), 3)
        self.assertIn("Welcome to Python", associated[0][1])
        self.assertNotIn("Variables", associated[0][1])
        self.assertIn("Variables in Python", associated[1][1])
        self.assertIn("Functions define reusable code", associated[2][1])

    def test_ai_chapter_detection_when_official_unavailable(self):
        """Scenario 2: Video without official chapters -> AI divides transcript into logical topic chapters labeled is_ai_detected=True."""
        metadata = VideoMetadata(
            id="vid_no_official",
            title="Complete Web Development Guide",
            thumbnail="https://example.com/thumb.jpg",
            duration=900,  # 15 minutes
            chapters=None
        )
        # Create segments spanning 900 seconds
        segments = []
        for sec in range(0, 900, 30):
            segments.append({
                "start": float(sec),
                "duration": 25.0,
                "text": f"At second {sec}, we discuss topic details."
            })
        transcript = NormalizedTranscript(
            text=" ".join(s["text"] for s in segments),
            language="English",
            language_code="en",
            is_generated=True,
            segments=segments
        )

        detected = chapter_service.detect_or_generate_chapters(metadata, transcript, llm_provider=None)
        self.assertTrue(len(detected) >= 3, f"Expected at least 3 chapters, got {len(detected)}")
        for ch in detected:
            self.assertTrue(ch.is_ai_detected, f"Chapter {ch.title} should be marked is_ai_detected=True")
            self.assertIsNotNone(ch.timestamp_str)
            self.assertIsNotNone(ch.duration_str)
        self.assertEqual(detected[0].start_time, 0.0)

    def test_llm_driven_ai_chapter_detection(self):
        """Verify LLM chapter detection parse and formatting when LLM provides topic breaks."""
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.provider_name = "mock-ai"
        mock_provider.generate_content.return_value = json.dumps([
            {"title": "Getting Started with React", "start_time": 0.0},
            {"title": "State Management with Hooks", "start_time": 300.0},
            {"title": "Building Custom Hooks", "start_time": 720.0}
        ])

        metadata = VideoMetadata(
            id="vid_react",
            title="React 19 Deep Dive",
            thumbnail="https://example.com/thumb.jpg",
            duration=1200
        )
        segments = [
            {"start": 0.0, "duration": 5.0, "text": "React 19 introduction."},
            {"start": 320.0, "duration": 5.0, "text": "State management hooks."},
            {"start": 750.0, "duration": 5.0, "text": "Custom hook design."}
        ]
        transcript = NormalizedTranscript(
            text="React 19 introduction. State management hooks. Custom hook design.",
            language="English",
            language_code="en",
            is_generated=False,
            segments=segments
        )

        detected = chapter_service.detect_or_generate_chapters(metadata, transcript, llm_provider=mock_provider)
        self.assertEqual(len(detected), 3)
        self.assertTrue(detected[0].is_ai_detected)
        self.assertEqual(detected[0].title, "Getting Started with React")
        self.assertEqual(detected[1].title, "State Management with Hooks")
        self.assertEqual(detected[1].start_time, 300.0)
        self.assertEqual(detected[1].end_time, 720.0)

    def test_summarization_service_chapter_methods(self):
        """Verify SummarizationService methods for Overview, Chapter Notes, and Final Revision."""
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.provider_name = "test-ai"
        mock_provider.model_name = "test-model"

        mock_provider.generate_content.side_effect = [
            # 1. Overview
            "# Python Guide\n\n## Video Overview\nCovers Python core.\n### Learning Objectives\n- Learn syntax\n### Key Takeaways\n- Readable code\n### Prerequisites\nNone",
            # 2. Chapter 1
            "## Chapter 1: Introduction\n**Timestamp:** 00:00 – 02:00\n**Duration:** 2 minutes\n### 1. Chapter Summary\nIntro to Python.\n### 2. Key Concepts\n- **Syntax**: Clean and readable\n### 3. Important Details\n- Dynamic typing\n### 4. Practical Examples\nprint('hello')\n### 5. Key Takeaways\n- Easy syntax\n### 6. Important Terms\n- **Interpreter**: Executes code",
            # 3. Final Revision
            "## Final Revision\n### 1. Complete Video Summary\nPython is powerful.\n### 2. Most Important Concepts\n- Syntax\n### 3. Quick Revision Notes\n- Rapid dev\n### 4. Glossary\n- **Python**: High-level language\n### 5. Questions for Self-Assessment\n1. What is Python?\n#### Answers\n1. A high-level language."
        ]

        service = SummarizationService(provider=mock_provider)
        
        overview = service.generate_video_overview("Python Guide", "10 minutes", "Sample context")
        self.assertIn("## Video Overview", overview)
        self.assertIn("Learning Objectives", overview)

        ch1_notes = service.generate_chapter_notes(
            chapter_num=1,
            chapter_title="Introduction",
            timestamp_str="00:00 – 02:00",
            duration_str="2 minutes",
            transcript_text="Sample intro transcript text."
        )
        self.assertIn("## Chapter 1: Introduction", ch1_notes)
        self.assertIn("1. Chapter Summary", ch1_notes)
        self.assertIn("2. Key Concepts", ch1_notes)
        self.assertIn("6. Important Terms", ch1_notes)

        revision = service.generate_final_revision("Python Guide", ch1_notes)
        self.assertIn("## Final Revision", revision)
        self.assertIn("5. Questions for Self-Assessment", revision)

        full_doc = service.build_full_markdown(overview, [ChapterItem(title="Intro", start_time=0.0, content=ch1_notes)], revision)
        self.assertIn("## Video Overview", full_doc)
        self.assertIn("## Chapter 1: Introduction", full_doc)
        self.assertIn("## Final Revision", full_doc)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.openai.OpenAIProvider.generate_content")
    def test_full_chapter_notes_pipeline(self, mock_gen, mock_get_transcript, mock_get_metadata):
        """End-to-end notes generation verifies overview, all chapters, and revision section."""
        mock_get_metadata.return_value = VideoMetadata(
            id="pipeline_vid",
            title="TypeScript in 2026",
            thumbnail="https://example.com/thumb.jpg",
            duration=360,
            chapters=[
                ChapterItem(title="Getting Started", start_time=0.0, end_time=180.0, is_ai_detected=False),
                ChapterItem(title="Generics and Types", start_time=180.0, end_time=360.0, is_ai_detected=False)
            ]
        )
        mock_get_transcript.return_value = NormalizedTranscript(
            text="TypeScript intro. Now generics and strict types.",
            language="English",
            language_code="en",
            is_generated=False,
            segments=[
                {"start": 10.0, "duration": 5.0, "text": "TypeScript intro."},
                {"start": 200.0, "duration": 5.0, "text": "Now generics and strict types."}
            ]
        )
        mock_gen.return_value = "# TypeScript in 2026\n\n## Overview\nCovers type safety.\n### 1. Summary\nDetails."

        resp = notes_service.generate(
            url="https://www.youtube.com/watch?v=pipeline_vid",
            provider="openai",
            model="gpt-4o-mini",
            api_key="valid-key"
        )

        self.assertTrue(resp.success)
        self.assertIsNotNone(resp.overview_content)
        self.assertIsNotNone(resp.revision_content)
        self.assertEqual(len(resp.chapters), 2)
        self.assertEqual(resp.chapters[0].title, "Getting Started")
        self.assertEqual(resp.chapters[1].title, "Generics and Types")
        self.assertIsNotNone(resp.chapters[0].content)
        self.assertIsNotNone(resp.notes)
        self.assertIn("Overview", resp.notes.content)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.llm.openai.OpenAIProvider.generate_content")
    def test_streaming_endpoint(self, mock_gen, mock_get_transcript, mock_get_metadata):
        """Verify POST /api/notes/generate-stream streams Server-Sent Events with progressive chapter updates."""
        mock_get_metadata.return_value = VideoMetadata(
            id="stream_vid",
            title="Streaming Architecture",
            thumbnail="https://example.com/thumb.jpg",
            duration=300,
            chapters=[
                ChapterItem(title="SSE Basics", start_time=0.0, end_time=150.0, is_ai_detected=False),
                ChapterItem(title="WebSocket vs SSE", start_time=150.0, end_time=300.0, is_ai_detected=False)
            ]
        )
        mock_get_transcript.return_value = NormalizedTranscript(
            text="SSE uses standard HTTP. WebSockets allow bi-directional comms.",
            language="English",
            language_code="en",
            is_generated=False,
            segments=[
                {"start": 5.0, "duration": 10.0, "text": "SSE uses standard HTTP."},
                {"start": 160.0, "duration": 10.0, "text": "WebSockets allow bi-directional comms."}
            ]
        )
        mock_gen.return_value = "Content for streaming segment."

        response = self.client.post("/api/notes/generate-stream", json={
            "youtube_url": "https://www.youtube.com/watch?v=stream_vid",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key": "valid-key"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        
        # Parse SSE events from response text
        raw_text = response.text
        lines = [line.strip() for line in raw_text.splitlines() if line.startswith("data: ")]
        self.assertTrue(len(lines) >= 5, f"Expected multiple SSE events, got: {len(lines)}")

        event_types = []
        for line in lines:
            payload = json.loads(line[6:])
            event_types.append(payload.get("type"))

        self.assertIn("status", event_types)
        self.assertIn("metadata", event_types)
        self.assertIn("overview", event_types)
        self.assertIn("chapter_start", event_types)
        self.assertIn("chapter_complete", event_types)
        self.assertIn("revision", event_types)
        self.assertIn("complete", event_types)

if __name__ == "__main__":
    unittest.main()
