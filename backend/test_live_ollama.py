import sys
from unittest.mock import patch
from app.models.schemas import VideoMetadata, ChapterItem
from app.models.transcript import NormalizedTranscript
from app.services.notes_service import notes_service

def test_live_ollama():
    print("Testing full notes_service.generate with live Ollama...", flush=True)
    with patch("app.services.notes_service.youtube_service.get_video_metadata") as mock_meta, \
         patch("app.services.notes_service.transcript_service.get_transcript") as mock_trans:
        mock_meta.return_value = VideoMetadata(
            id="vid_live_test",
            title="Python Functions and Modules",
            thumbnail="https://img.youtube.com/vi/vid_live_test/0.jpg",
            duration=300,
            chapters=[
                ChapterItem(title="Defining Functions", start_time=0.0, end_time=150.0, is_ai_detected=False),
                ChapterItem(title="Importing Modules", start_time=150.0, end_time=300.0, is_ai_detected=False),
            ]
        )
        mock_trans.return_value = NormalizedTranscript(
            text=(
                "In this lesson we define functions in Python using def keyword. Functions can take arguments and return values. "
                "Next we look at importing modules like math and os to organize clean code."
            ),
            language="English",
            language_code="en",
            is_generated=False,
            segments=[
                {"start": 10.0, "duration": 20.0, "text": "In this lesson we define functions in Python using def keyword. Functions take arguments."},
                {"start": 160.0, "duration": 20.0, "text": "Next we look at importing modules like math and os to organize clean code."}
            ]
        )

        resp = notes_service.generate(
            url="https://www.youtube.com/watch?v=vid_live_test",
            provider="ollama",
            model="qwen3:1.7b",
            api_key=""
        )

        print(f"Success: {resp.success}", flush=True)
        print(f"Provider: {resp.provider}", flush=True)
        print(f"Model: {resp.model}", flush=True)
        print(f"Overview Present: {bool(resp.overview_content)}", flush=True)
        print(f"Chapters Count: {len(resp.chapters) if resp.chapters else 0}", flush=True)
        print(f"Revision Present: {bool(resp.revision_content)}", flush=True)
        if resp.notes:
            print(f"Title: {resp.notes.title}", flush=True)
            print(f"Notes Length: {len(resp.notes.content)} chars", flush=True)
            print("Preview:\n", resp.notes.content[:350], flush=True)

        assert resp.success is True, f"Failed: {resp.error}"
        assert resp.provider == "ollama"
        assert resp.model == "qwen3:1.7b"
        assert resp.notes is not None
        assert len(resp.chapters) == 2
        assert len(resp.notes.content) > 100
        print("\n>> LIVE OLLAMA PIPELINE TEST PASSED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    test_live_ollama()
