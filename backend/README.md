# NoteTube Backend
FastAPI backend service supporting local LLM inference via Ollama and dynamic cloud providers.

## Preflight Diagnostic Check
Before launching the server, verify your local Ollama installation:

```bash
python check_ollama.py
```

## Running the Backend Server
```bash
python -m uvicorn app.main:app --port 8000 --reload
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- Ollama Health/Status: `GET /api/ollama/status`
- Provider Validation: `POST /api/providers/validate`
- Video Preload & Cache: `POST /api/video/load`
- Quick Summary: `POST /api/modes/quick-summary`
- Detailed Notes: `POST /api/modes/detailed-notes`
- Chapter Slides & PPTX: `POST /api/slides/generate`
- Transcript RAG Chatbot: `POST /api/rag/ask`

## Testing
```bash
# Run complete test suite (55 tests)
python -m pytest -v

# Run targeted test suites
python -m pytest test_new_features.py -v
python -m pytest test_all_scenarios.py -v
python -m pytest test_slide_service.py -v
```
