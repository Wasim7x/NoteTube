import unittest
from unittest.mock import MagicMock, patch
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    TranslationLanguageNotAvailable,
)
from app.services.transcript_service import transcript_service
from app.services.notes_service import notes_service
from app.models.schemas import VideoMetadata
from app.models.transcript import NormalizedTranscript

class FakeTranslationLanguage:
    def __init__(self, language: str, language_code: str):
        self.language = language
        self.language_code = language_code

class FakeTranscriptTrack:
    def __init__(
        self,
        video_id: str,
        language: str,
        language_code: str,
        is_generated: bool = False,
        is_translatable: bool = True,
        translation_languages=None,
        snippets=None
    ):
        self.video_id = video_id
        self.language = language
        self.language_code = language_code
        self.is_generated = is_generated
        self.is_translatable = is_translatable
        self.translation_languages = translation_languages or []
        self._snippets = snippets or [
            {"text": f"This is sample speech in {language}.", "start": 0.0, "duration": 2.5},
            {"text": "Continuing technical explanation.", "start": 2.5, "duration": 3.0}
        ]

    def fetch(self):
        return self._snippets

    def translate(self, lang_code: str):
        valid_codes = [tl.language_code for tl in self.translation_languages]
        if lang_code not in valid_codes:
            raise TranslationLanguageNotAvailable(self.video_id)
        return FakeTranscriptTrack(
            video_id=self.video_id,
            language=f"Translated ({lang_code})",
            language_code=lang_code,
            is_generated=True,
            snippets=[
                {"text": f"Translated text into {lang_code}.", "start": 0.0, "duration": 2.5}
            ]
        )


class TestTranscriptService(unittest.TestCase):

    @patch("app.services.transcript_service.YouTubeTranscriptApi")
    def test_1_english_transcript_selected(self, mock_api_cls):
        """Test 1: English transcript available -> automatically selected -> successful extraction."""
        mock_instance = MagicMock()
        mock_api_cls.return_value = mock_instance

        track_en = FakeTranscriptTrack(
            video_id="vid_en",
            language="English",
            language_code="en",
            is_generated=False
        )
        mock_instance.list.return_value = [track_en]

        result = transcript_service.get_transcript("vid_en")
        self.assertIsNotNone(result)
        self.assertEqual(result.language, "English")
        self.assertEqual(result.language_code, "en")
        self.assertFalse(result.is_generated)
        self.assertIn("sample speech in English", result.text)
        self.assertEqual(len(result.segments), 2)
        self.assertEqual(result.segments[0]["start"], 0.0)

    @patch("app.services.transcript_service.YouTubeTranscriptApi")
    def test_2_non_english_transcript_selected(self, mock_api_cls):
        """Test 2: English unavailable, Hindi/Spanish available -> automatically selected -> successful extraction."""
        mock_instance = MagicMock()
        mock_api_cls.return_value = mock_instance

        track_hi = FakeTranscriptTrack(
            video_id="vid_hi",
            language="Hindi",
            language_code="hi",
            is_generated=False
        )
        mock_instance.list.return_value = [track_hi]

        result = transcript_service.get_transcript("vid_hi")
        self.assertIsNotNone(result)
        self.assertEqual(result.language, "Hindi")
        self.assertEqual(result.language_code, "hi")
        self.assertIn("sample speech in Hindi", result.text)

    @patch("app.services.transcript_service.YouTubeTranscriptApi")
    def test_3_auto_generated_transcript_selected(self, mock_api_cls):
        """Test 3: Only auto-generated captions available -> automatically selected."""
        mock_instance = MagicMock()
        mock_api_cls.return_value = mock_instance

        track_auto = FakeTranscriptTrack(
            video_id="vid_auto",
            language="Spanish (auto-generated)",
            language_code="es",
            is_generated=True
        )
        mock_instance.list.return_value = [track_auto]

        result = transcript_service.get_transcript("vid_auto")
        self.assertIsNotNone(result)
        self.assertEqual(result.language_code, "es")
        self.assertTrue(result.is_generated)
        self.assertIn("sample speech in Spanish", result.text)

    @patch("app.services.transcript_service.YouTubeTranscriptApi")
    def test_4_multiple_languages_deterministic_selection(self, mock_api_cls):
        """Test 4: Multiple transcript tracks -> deterministic best transcript selected."""
        mock_instance = MagicMock()
        mock_api_cls.return_value = mock_instance

        # Case A: Manual Spanish vs Auto English -> Manual Spanish wins (Manual > Auto)
        manual_es = FakeTranscriptTrack("vid_multi", "Spanish", "es", is_generated=False)
        auto_en = FakeTranscriptTrack("vid_multi", "English (auto)", "en", is_generated=True)
        mock_instance.list.return_value = [auto_en, manual_es]

        result = transcript_service.get_transcript("vid_multi")
        self.assertIsNotNone(result)
        self.assertEqual(result.language_code, "es")
        self.assertFalse(result.is_generated)

        # Case B: Auto en-US vs Auto Hindi -> Auto en-US wins
        auto_en_us = FakeTranscriptTrack("vid_multi2", "English (US)", "en-US", is_generated=True)
        auto_hi = FakeTranscriptTrack("vid_multi2", "Hindi (auto)", "hi", is_generated=True)
        mock_instance.list.return_value = [auto_hi, auto_en_us]

        result2 = transcript_service.get_transcript("vid_multi2")
        self.assertIsNotNone(result2)
        self.assertEqual(result2.language_code, "en-US")

    @patch("app.services.transcript_service.YouTubeTranscriptApi")
    def test_5_translation_unavailable_no_failure(self, mock_api_cls):
        """Test 5: Requested translation unavailable -> no failure -> original transcript used."""
        mock_instance = MagicMock()
        mock_api_cls.return_value = mock_instance

        track_hi = FakeTranscriptTrack(
            video_id="vid_trans",
            language="Hindi",
            language_code="hi",
            is_generated=True,
            is_translatable=True,
            translation_languages=[FakeTranslationLanguage("French", "fr")]
        )
        mock_instance.list.return_value = [track_hi]

        # Request translation to 'en', which is NOT in translation_languages
        result = transcript_service.get_transcript("vid_trans", target_language="en")
        self.assertIsNotNone(result)
        # Succeeded without failure and used original transcript language
        self.assertEqual(result.language_code, "hi")
        self.assertIn("sample speech in Hindi", result.text)

    @patch("app.services.notes_service.transcript_service.get_transcript")
    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    def test_6_no_transcript_fallback_pipeline(self, mock_get_metadata, mock_get_transcript):
        """Test 6: No captions -> fallback pipeline engaged -> request does not fail with 400."""
        mock_get_metadata.return_value = VideoMetadata(
            id="vid_nocap",
            title="Advanced System Architecture",
            thumbnail="https://example.com/thumb.jpg",
            description="Comprehensive guide covering database indexing, caching strategies, and event-driven architecture.",
            duration=1200
        )
        mock_get_transcript.return_value = None  # No transcript found

        with patch("app.services.llm.gemini.GeminiProvider.generate_content") as mock_gen:
            mock_gen.return_value = "# Advanced System Architecture Notes\n\n## Overview\nSynthesized from course syllabus."
            resp = notes_service.generate(
                url="https://www.youtube.com/watch?v=vid_nocap",
                provider="gemini",
                model="gemini-2.5-flash",
                api_key="mock-key"
            )

            self.assertTrue(resp.success)
            self.assertTrue(resp.fallback_used)
            self.assertFalse(resp.transcript_available)
            self.assertIsNone(resp.transcript_language)
            self.assertIsNotNone(resp.notes)
            self.assertIn("Advanced System Architecture Notes", resp.notes.title)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    def test_7_existing_failing_video_SahaDGzN_Bk(self, mock_get_metadata):
        """
        Test 7: Test with the previously failing video ID (SahaDGzN-Bk).
        Verifies that 'The requested translation language is not available' failure no longer occurs.
        """
        mock_get_metadata.return_value = VideoMetadata(
            id="SahaDGzN-Bk",
            title="Offline Evals Vs Online Evals | CampusX",
            thumbnail="https://img.youtube.com/vi/SahaDGzN-Bk/maxresdefault.jpg"
        )

        # Test live transcript extraction for SahaDGzN-Bk
        result = transcript_service.get_transcript("SahaDGzN-Bk")
        self.assertIsNotNone(result, "Transcript extraction should not be None for SahaDGzN-Bk")
        self.assertIn(result.language_code, ["en-US", "hi"])
        self.assertTrue(len(result.text) > 1000)

        # Test end-to-end notes generation pipeline with LLM mocked
        with patch("app.services.llm.openai.OpenAIProvider.generate_content") as mock_gen:
            mock_gen.return_value = "# Offline Evals Vs Online Evals Notes\n\n## Overview\nEvaluation strategies."
            resp = notes_service.generate(
                url="https://www.youtube.com/watch?v=SahaDGzN-Bk",
                provider="openai",
                model="gpt-4o-mini",
                api_key="mock-key-12345"
            )

            self.assertTrue(resp.success)
            self.assertFalse(resp.fallback_used)
            self.assertTrue(resp.transcript_available)
            self.assertIsNotNone(resp.transcript_language)
            self.assertIsNotNone(resp.notes)

    def test_8_api_endpoint_generate_success_and_fallback(self):
        """Test 8: Verify POST /api/notes/generate returns 200 with transcript metadata and doesn't fail on no-transcript."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Normal transcript flow via API
        with patch("app.services.notes_service.transcript_service.get_transcript") as mock_t, \
             patch("app.services.notes_service.youtube_service.get_video_metadata") as mock_m, \
             patch("app.services.llm.openai.OpenAIProvider.generate_content") as mock_gen:
            
            mock_m.return_value = VideoMetadata(
                id="test_api_vid",
                title="API Test Video",
                thumbnail="https://example.com/thumb.jpg"
            )
            mock_t.return_value = NormalizedTranscript(
                text="This is an informative tutorial on API design and microservices architecture.",
                language="English",
                language_code="en",
                is_generated=False,
                source="youtube"
            )
            mock_gen.return_value = "# API Design Notes\n\n## Overview\nMicroservices basics."

            response = client.post("/api/notes/generate", json={
                "youtube_url": "https://www.youtube.com/watch?v=test_api_vid",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key": "valid-key-123"
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertFalse(data["fallback_used"])
            self.assertTrue(data["transcript_available"])
            self.assertEqual(data["transcript_language"], "English")
            self.assertEqual(data["transcript_language_code"], "en")
            self.assertFalse(data["transcript_generated"])

        # Fallback flow via API (no transcript available)
        with patch("app.services.notes_service.transcript_service.get_transcript") as mock_t, \
             patch("app.services.notes_service.youtube_service.get_video_metadata") as mock_m, \
             patch("app.services.llm.openai.OpenAIProvider.generate_content") as mock_gen:
            
            mock_m.return_value = VideoMetadata(
                id="test_nocap_api",
                title="Syllabus Only Video",
                thumbnail="https://example.com/thumb.jpg",
                description="Introductory module explaining cloud concepts."
            )
            mock_t.return_value = None
            mock_gen.return_value = "# Syllabus Only Notes\n\n## Overview\nCloud concepts."

            response_fallback = client.post("/api/notes/generate", json={
                "youtube_url": "https://www.youtube.com/watch?v=test_nocap_api",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key": "valid-key-123"
            })

            self.assertEqual(response_fallback.status_code, 200)
            data_fb = response_fallback.json()
            self.assertTrue(data_fb["success"])
            self.assertTrue(data_fb["fallback_used"])
            self.assertFalse(data_fb["transcript_available"])
            self.assertIsNone(data_fb["transcript_language"])


if __name__ == "__main__":
    unittest.main()

