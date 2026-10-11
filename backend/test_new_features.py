import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.llm.connection_test import test_provider_connection as check_conn
from app.services.rag_service import rag_service, LocalTFIDFEmbedder
from app.services.video_service import video_job_service
from app.models.schemas import VideoMetadata, ChapterItem

client = TestClient(app)

TEST_VIDEO_ID = "testvid1234"  # Exact 11 characters standard YouTube ID

def test_local_tfidf_embedder():
    embedder = LocalTFIDFEmbedder(dim=128)
    v1 = embedder.embed_text("React hooks useState useEffect")
    v2 = embedder.embed_text("React functional component useState")
    v3 = embedder.embed_text("Cooking chocolate chip cookies with butter")

    import numpy as np
    score_similar = float(np.dot(v1, v2))
    score_different = float(np.dot(v1, v3))

    assert len(v1) == 128
    assert score_similar > score_different
    assert score_similar > 0.3

def test_connection_testing_ollama_live():
    res = check_conn(
        provider="ollama",
        model="qwen3:1.7b"
    )
    assert res["success"] is True
    assert "ollama" in res["provider"]

def test_connection_testing_missing_key():
    res = check_conn(
        provider="openai",
        model="gpt-4o-mini",
        api_key=""
    )
    assert res["success"] is False
    assert "API key" in res["error"]


def test_provider_validate_endpoint():
    res = client.post("/api/providers/validate", json={
        "provider": "ollama",
        "model": "qwen3:1.7b"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True

def test_video_load_and_caching():
    mock_meta = VideoMetadata(
        id=TEST_VIDEO_ID,
        title="Test Architecture Video",
        thumbnail="https://example.com/thumb.jpg",
        duration=300,
        chapters=[
            ChapterItem(chapter_id="ch_1", title="Intro", start_time=0.0, end_time=120.0),
            ChapterItem(chapter_id="ch_2", title="Deep Dive", start_time=120.0, end_time=300.0)
        ]
    )

    with patch("app.services.youtube_service.youtube_service.get_video_metadata", return_value=mock_meta), \
         patch("app.services.transcript_service.transcript_service.get_transcript") as mock_ts:
        
        mock_ts_obj = MagicMock()
        mock_ts_obj.__str__.return_value = "Hello and welcome to this video about architecture. In this chapter we build components."
        mock_ts_obj.language = "English"
        mock_ts_obj.language_code = "en"
        mock_ts_obj.is_generated = False
        mock_ts_obj.segments = [
            {"text": "Hello and welcome to this video", "start": 0.0, "duration": 5.0},
            {"text": "about architecture.", "start": 5.0, "duration": 4.0},
            {"text": "In this chapter we build components.", "start": 125.0, "duration": 6.0}
        ]
        mock_ts.return_value = mock_ts_obj

        # Test video loading
        res = client.post("/api/video/load", json={"youtube_url": f"https://www.youtube.com/watch?v={TEST_VIDEO_ID}"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["video_id"] == TEST_VIDEO_ID
        assert data["transcript_available"] is True
        assert len(data["chapters"]) == 2

        # Verify caching
        cached_res = client.get(f"/api/video/{TEST_VIDEO_ID}")
        assert cached_res.status_code == 200
        assert cached_res.json()["video_id"] == TEST_VIDEO_ID

def test_quick_summary_mode():
    with patch("app.services.summarization_service.SummarizationService.generate_quick_summary", return_value="""# Quick Summary: Test Architecture Video

## Executive Overview
This video provides a concise overview of software architecture.

## Core Concepts & Highlights
- **Microservices**: Decomposed services.
- **REST**: Stateless HTTP APIs.

## Key Takeaways
- Decoupling improves scale.
- Fast deployments.
"""):
        res = client.post("/api/modes/quick-summary", json={
            "video_id": TEST_VIDEO_ID,
            "provider": "ollama",
            "model": "qwen3:1.7b"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "Test Architecture Video" in data["title"]
        assert len(data["key_takeaways"]) > 0

def test_detailed_notes_mode():
    with patch("app.services.summarization_service.SummarizationService.generate_detailed_notes", return_value="""# Comprehensive Study Notes: Test Architecture Video

## Video Overview & Conceptual Scope
Detailed notes about system architecture.
"""):
        res = client.post("/api/modes/detailed-notes", json={
            "video_id": TEST_VIDEO_ID,
            "provider": "ollama",
            "model": "qwen3:1.7b"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "Test Architecture Video" in data["title"]

def test_rag_chatbot_query_and_grounding():
    with patch("app.services.llm.ollama.OllamaProvider.generate_content", return_value="The video explains architecture at [00:00]."):
        res = client.post("/api/rag/ask", json={
            "video_id": TEST_VIDEO_ID,
            "query": "What is discussed about architecture?",
            "provider": "ollama",
            "model": "qwen3:1.7b"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["grounded"] is True
        assert len(data["sources"]) > 0

def test_rag_unrelated_query_rejection():
    res = client.post("/api/rag/ask", json={
        "video_id": TEST_VIDEO_ID,
        "query": "How do you bake a pineapple pizza with yeast and mozzarella?",
        "provider": "ollama",
        "model": "qwen3:1.7b"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["grounded"] is False
    assert "not discussed or mentioned" in data["answer"]

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NoteTube"

def test_api_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NoteTube"

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NoteTube"
    assert "message" in data

def test_cors_origin_port_5174():
    res = client.get("/health", headers={"Origin": "http://localhost:5174"})
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5174"

    res_127 = client.get("/health", headers={"Origin": "http://127.0.0.1:5174"})
    assert res_127.status_code == 200
    assert res_127.headers.get("access-control-allow-origin") == "http://127.0.0.1:5174"

