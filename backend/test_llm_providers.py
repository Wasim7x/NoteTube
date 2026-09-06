import sys
import unittest
from unittest.mock import MagicMock, patch

from app.services.llm.registry import PROVIDER_METADATA, get_all_providers_info, get_registered_provider_class
from app.services.llm.factory import create_llm_provider
from app.services.llm.base import LLMProvider
from app.services.summarization_service import SummarizationService
from app.services.notes_service import notes_service
from app.models.schemas import GenerateNotesRequest, VideoMetadata
from fastapi.testclient import TestClient
from app.main import app

class TestLLMProviders(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_providers_endpoint(self):
        """Verify GET /api/providers returns all 5 supported providers and models."""
        response = self.client.get("/api/providers")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("providers", data)
        provider_ids = [p["id"] for p in data["providers"]]
        self.assertIn("openai", provider_ids)
        self.assertIn("gemini", provider_ids)
        self.assertIn("anthropic", provider_ids)
        self.assertIn("groq", provider_ids)
        self.assertIn("openrouter", provider_ids)

        for p in data["providers"]:
            self.assertTrue(len(p["models"]) > 0, f"Provider {p['id']} has no models")
            self.assertTrue(bool(p["default_model"]), f"Provider {p['id']} has no default model")
            self.assertTrue(bool(p["key_placeholder"]))

    def test_factory_validation(self):
        """Verify factory enforces provider, model, and api key constraints."""
        with self.assertRaises(ValueError) as ctx:
            create_llm_provider(provider="", model="gpt-4o", api_key="sk-test")
        self.assertIn("Provider must be specified", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            create_llm_provider(provider="unsupported_xyz", model="m", api_key="key")
        self.assertIn("Unsupported provider", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            create_llm_provider(provider="openai", model="gpt-4o", api_key="")
        self.assertIn("API key is required", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            create_llm_provider(provider="gemini", model="gemini-2.5-flash", api_key="   ")
        self.assertIn("API key is required", str(ctx.exception))

    def test_factory_instantiation(self):
        """Verify factory instantiates the correct adapter class for each supported provider."""
        providers_to_test = ["openai", "gemini", "anthropic", "groq", "openrouter"]
        for pid in providers_to_test:
            provider_inst = create_llm_provider(
                provider=pid,
                model="",
                api_key="mock-key-12345"
            )
            self.assertEqual(provider_inst.provider_name, pid)
            self.assertTrue(bool(provider_inst.model_name))

    def test_summarization_with_provider_injection(self):
        """Verify SummarizationService works seamlessly with any injected LLMProvider."""
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.provider_name = "mock-ai"
        mock_provider.model_name = "mock-model"
        mock_provider.generate_content.return_value = "# Note Title\n\n- Key point 1\n- Key point 2"

        service = SummarizationService(provider=mock_provider)
        sample_transcript = "In this video we discuss python architecture and clean coding practices. " * 10
        notes = service.generate_notes(sample_transcript)

        self.assertIn("# Note Title", notes)
        mock_provider.generate_content.assert_called()

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    def test_notes_service_multiple_providers(self, mock_get_transcript, mock_get_metadata):
        """Test full notes generation pipeline across multiple providers (OpenAI, Groq, Anthropic, Gemini, OpenRouter)."""
        mock_get_metadata.return_value = VideoMetadata(
            id="test12345",
            title="Clean Code Tutorial",
            thumbnail="https://example.com/thumb.jpg"
        )
        mock_get_transcript.return_value = "This is a detailed tutorial about software architecture and clean code. " * 10

        provider_classes = {
            "openai": ("app.services.llm.openai.OpenAIProvider.generate_content", "gpt-4o-mini"),
            "groq": ("app.services.llm.groq.GroqProvider.generate_content", "llama-3.3-70b-versatile"),
            "anthropic": ("app.services.llm.anthropic.AnthropicProvider.generate_content", "claude-3-7-sonnet-latest"),
            "gemini": ("app.services.llm.gemini.GeminiProvider.generate_content", "gemini-2.5-flash"),
            "openrouter": ("app.services.llm.openrouter.OpenRouterProvider.generate_content", "deepseek/deepseek-chat"),
        }

        for pid, (target_path, model) in provider_classes.items():
            with patch(target_path) as mock_gen:
                mock_gen.return_value = f"# Clean Architecture Notes ({pid})\n\n- Modular design\n- Separation of concerns"
                
                resp = notes_service.generate(
                    url="https://www.youtube.com/watch?v=test12345",
                    provider=pid,
                    model=model,
                    api_key="valid-test-key-999"
                )

                self.assertTrue(resp.success, f"Failed for provider {pid}: {resp.error}")
                self.assertEqual(resp.provider, pid)
                self.assertEqual(resp.model, model)
                self.assertIsNotNone(resp.notes)
                self.assertIn("Clean Architecture Notes", resp.notes.title)
                self.assertIn("Modular design", resp.notes.content)

    @patch("app.services.notes_service.youtube_service.get_video_metadata")
    @patch("app.services.notes_service.transcript_service.get_transcript")
    def test_invalid_api_key_error_handling(self, mock_get_transcript, mock_get_metadata):
        """Verify invalid API key errors are caught and returned as clean user messages without exposing the key."""
        mock_get_metadata.return_value = VideoMetadata(
            id="test12345",
            title="Clean Code Tutorial",
            thumbnail="https://example.com/thumb.jpg"
        )
        mock_get_transcript.return_value = "This is a detailed tutorial about software architecture. " * 10

        secret_key = "super_secret_bad_key_xyz987"
        
        with patch("app.services.llm.openai.OpenAIProvider.generate_content") as mock_gen:
            mock_gen.side_effect = ValueError("The provided OpenAI API key is invalid or unauthorized.")
            
            resp = notes_service.generate(
                url="https://www.youtube.com/watch?v=test12345",
                provider="openai",
                model="gpt-4o-mini",
                api_key=secret_key
            )

            self.assertFalse(resp.success)
            self.assertIn("invalid or unauthorized", resp.error)
            self.assertNotIn(secret_key, resp.error)

    def test_notes_route_validation(self):
        """Verify POST /api/notes/generate validates missing fields before reaching LLM."""
        response = self.client.post("/api/notes/generate", json={
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "provider": "",
            "model": "gpt-4o-mini",
            "api_key": ""
        })
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
