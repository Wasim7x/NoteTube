# NoteTube - Dynamic AI YouTube Notes Assistant

NoteTube is an intelligent AI assistant that transforms any YouTube video into structured, comprehensive, and beautiful markdown study notes.

Unlike traditional implementations that rely on hardcoded API keys and single-model configurations in server `.env` files, **NoteTube is completely provider-agnostic and dynamically configured directly from the frontend UI**.

---

## 🌟 Key Features

- **Dynamic Provider Selection**: Switch between leading AI providers on-the-fly without restarting the server or altering `.env` files.
- **Out-of-the-Box Supported Providers**:
  - **Google Gemini** (`gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`)
  - **OpenAI** (`gpt-4o-mini`, `gpt-4o`, `gpt-4.5-preview`, `o3-mini`, `o1-mini`)
  - **Anthropic Claude** (`claude-3-7-sonnet-latest`, `claude-3-5-sonnet-latest`, `claude-3-5-haiku-latest`, `claude-3-opus-latest`)
  - **Groq** (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`, `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`)
  - **OpenRouter** (`deepseek/deepseek-chat`, `deepseek/deepseek-r1`, `meta-llama/llama-3.3-70b-instruct`, `anthropic/claude-3.5-sonnet`)
- **Custom Model Support**: Choose preset models or input custom model IDs for any provider.
- **Provider-Agnostic Note Engine**: Uniform summarization prompt and chunking pipeline that works across all model architectures.
- **Zero-Storage Security Model**: API keys exist strictly in volatile frontend memory for the session; never persisted to `localStorage`, never logged, never returned in responses.
- **Export & Actions**: Download structured notes as Markdown (`.md`), export to PDF, or copy to clipboard with one click.

---

## 🔄 User Workflow

```text
Open Application (http://localhost:5173)
        ↓
Select AI Provider (e.g. Google Gemini, OpenAI, Groq, Anthropic, OpenRouter)
        ↓
Select Model Preset OR Enter Custom Model Name
        ↓
Enter API Key (with Show/Hide Toggle)
        ↓
Paste YouTube Video URL
        ↓
Click "Generate Notes"
        ↓
Backend fetches transcript & synthesizes structured notes using the selected provider
        ↓
View, Read, Copy, or Export Notes
```

---

## 🔒 Security Considerations

Treating user API keys as high-security credentials is foundational to NoteTube:

1. **No Persistent Storage**: API keys are **never stored** in `localStorage`, `sessionStorage`, cookies, or databases.
2. **Sanitized Logs**: Backend request logging masks and omits API keys entirely. No key values appear in terminal or log files.
3. **No Key Echoing**: API error responses never echo or expose the key.
4. **Clean Error Mapping**: Provider errors (such as `AuthenticationError`, `RateLimitError`, `NotFoundError`) are captured inside adapters and translated into clean user-friendly alerts.
5. **HTTPS in Production**: All communications between frontend and backend in production should be served over TLS/HTTPS.

---

## 🏗 Architecture & Design

```text
+-------------------------------------------------------------+
|                        Frontend UI                          |
|  - ModelConfig (Provider Select, Model Select, Key Input)  |
|  - UrlInput (YouTube URL & Action Trigger)                  |
|  - NotesViewer (Markdown Viewer & Model Badge)             |
+------------------------------+------------------------------+
                               |
                               | POST /api/notes/generate
                               v
+-------------------------------------------------------------+
|                        FastAPI API                          |
|  - Validates YouTube URL, Provider, Model, and API Key      |
|  - GET /api/providers (Dynamic registry metadata)           |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                    LLM Provider Adapter                     |
|  - Common Interface: LLMProvider                            |
|  - Concrete Adapters:                                       |
|      * GeminiProvider                                       |
|      * OpenAIProvider                                       |
|      * AnthropicProvider                                    |
|      * GroqProvider                                         |
|      * OpenRouterProvider                                  |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                Summarization & Notes Engine                 |
|  - YouTube Metadata & Transcript Extractor                  |
|  - Text Chunker & Map-Reduce Summarizer                     |
|  - Uniform Structured Note-Generation Prompt                |
+-------------------------------------------------------------+
```

### Adding a New Provider

Adding another provider (e.g. Mistral, Cohere, DeepSeek) requires only 2 simple steps:

1. Create a provider adapter in `backend/app/services/llm/<provider>.py` implementing `LLMProvider`.
2. Register the provider and its metadata in `backend/app/services/llm/registry.py` and `backend/app/services/llm/factory.py`.

The frontend automatically receives the new provider and model options via `GET /api/providers`.

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10+ (or [uv](https://docs.astral.sh/uv/))
- **Node.js**: 18+ and `npm`

### 1. Backend Setup

```bash
cd backend

# Install dependencies with uv (or pip)
uv pip install -r requirements.txt

# Start FastAPI server
uv run uvicorn app.main:app --port 8000 --reload
```

Backend API will be accessible at: `http://localhost:8000`
Interactive API Docs: `http://localhost:8000/docs`

> Note: `.env` is **not required** for LLM keys. You only need `.env` if you want to configure `FRONTEND_URL` or server ports.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend will be accessible at: `http://localhost:5173`

---

## 🧪 Testing

### Backend Unit Tests

Run the automated test suite verifying provider registration, error sanitization, and multi-provider generation:

```bash
cd backend
uv run python test_llm_providers.py
```

### Frontend Build Verification

```bash
cd frontend
npm run build
```

---

## 📄 License

MIT License. Feel free to use, modify, and build upon NoteTube!
