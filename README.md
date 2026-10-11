# NoteTube - Dynamic AI YouTube Notes Assistant

NoteTube is an intelligent AI assistant that transforms any YouTube video into structured, comprehensive, and beautiful markdown study notes.

Unlike traditional implementations that rely on hardcoded API keys and single-model configurations in server `.env` files, **NoteTube is completely provider-agnostic and dynamically configured directly from the frontend UI**.

---

## 🌟 Key Features

- **Dynamic Provider Selection**: Switch between leading AI providers on-the-fly without restarting the server or altering `.env` files.
- **Out-of-the-Box Supported Providers**:
  - **Ollama (100% Local & Private)**: Run open-source models on your laptop with **zero cloud API keys** (`qwen3:1.7b`, `qwen3.5:latest`, `llama3.2:3b`, `mistral:7b`).
  - **Google Gemini** (`gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`)
  - **OpenAI** (`gpt-4o-mini`, `gpt-4o`, `gpt-4.5-preview`, `o3-mini`, `o1-mini`)
  - **Anthropic Claude** (`claude-3-7-sonnet-latest`, `claude-3-5-sonnet-latest`, `claude-3-5-haiku-latest`, `claude-3-opus-latest`)
  - **Groq** (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`, `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`)
  - **OpenRouter** (`deepseek/deepseek-chat`, `deepseek/deepseek-r1`, `meta-llama/llama-3.3-70b-instruct`, `anthropic/claude-3.5-sonnet`)
- **Custom Model Support**: Choose preset models or input custom model IDs for any provider.
- **Provider-Agnostic Note Engine**: Uniform summarization prompt and chunking pipeline that works across all model architectures.
- **Export & Actions**: Download structured notes as Markdown (`.md`), export to PDF, or copy to clipboard with one click.
- **Interactive Chapter Slides & PowerPoint (PPTX) Generation**:
  - Automatically extracts a representative video frame from every chapter (captured 5 seconds before the chapter end timestamp: `extraction_timestamp = max(chapter_start_time, chapter_end_time - 5)`).
  - Widescreen 16:9 presentation layout with proportional scaling preserving video aspect ratio.
  - Interactive slide previews accessible directly from each chapter heading (`[View Slide]`) and dedicated gallery.
  - One-click **Download PPT** with sanitized filenames.

---

## 🔄 User Workflow

```text
Open Application (http://localhost:5173)
        ↓
Select AI Provider:
  - Local Mode: Ollama (No API Key Required!)
  - Cloud Mode: Google Gemini, OpenAI, Groq, Anthropic, OpenRouter
        ↓
Select Model Preset (or custom model name)
        ↓
Paste YouTube Video URL
        ↓
Click "Generate Notes"
        ↓
Backend extracts transcript & synthesizes structured study notes
        ↓
Backend extracts chapter video frames (5s before chapter end) & builds 16:9 PPTX
        ↓
Interactive Slide Gallery & One-Click "Download PPT" (.pptx)
```


---

## 💻 Running 100% Locally with Ollama (Windows Guide)

NoteTube supports running completely offline and on-device using **Ollama**. In this mode:
- All LLM synthesis runs on your local machine.
- No cloud accounts, external API keys, or internet tokens are required.
- YouTube transcript processing and note generation remain identical to cloud mode.

### 1. Install Ollama on Windows
1. Download the Windows installer from [ollama.com/download/windows](https://ollama.com/download/windows).
2. Run the installer (`OllamaSetup.exe`). Once installed, Ollama runs in the background.

### 2. Download Compatible Models
Open PowerShell or Command Prompt and download your preferred model:

```bash
# Recommended for laptops (Fast & lightweight, ~1.4 GB)
ollama pull qwen3:1.7b

# High capability model (Requires ~6.6 GB VRAM/RAM)
ollama pull qwen3.5:latest

# Alternative lightweight Meta model (~2.0 GB)
ollama pull llama3.2:3b
```

### 3. Verify Installed Models
Check the models installed on your system:

```bash
ollama list
```

Verify that the model responds:

```bash
ollama run qwen3:1.7b "Hello! Are you ready?"
```

### 4. Configure Backend `.env`
Inside `backend/.env`, configure Ollama:

```env
# Local LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:1.7b
OLLAMA_TIMEOUT=120

# Application Configuration
FRONTEND_URL=http://localhost:5173
PORT=8000
HOST=0.0.0.0
```

### 5. Run the Preflight Check
Before launching, run NoteTube's preflight checker to verify Ollama status:

```bash
cd backend
python check_ollama.py
```

Expected output:
```text
[PASS] 1. Ollama CLI is installed and accessible in system PATH.
[PASS] 2. Ollama HTTP service is RUNNING at http://localhost:11434.
[PASS] 3. Retrieved installed model(s): qwen3:1.7b, qwen3.5:latest
[PASS] 4. Configured model 'qwen3:1.7b' is installed and READY.
>> ALL PREFLIGHT CHECKS PASSED!
```

---

## 🚀 Launching the Application

### Option A: From Project Root (Separate Terminals)

**Terminal 1 — Backend (FastAPI):**
```bash
cd backend
python -m uvicorn app.main:app --port 8000 --reload
```
*Backend API:* `http://localhost:8000`  
*Swagger Docs:* `http://localhost:8000/docs`  
*Ollama Status Endpoint:* `http://localhost:8000/api/ollama/status`

**Terminal 2 — Frontend (Vite):**
```bash
cd frontend
# On Windows PowerShell, use npm.cmd to bypass script execution restrictions:
npm.cmd run dev
```
*Frontend UI:* `http://localhost:5173`

---

## 🛠 Troubleshooting Ollama on Windows

### 1. Connection Error: `Could not connect to Ollama at http://localhost:11434`
- **Cause**: Ollama service is not running in the background.
- **Fix**: Launch Ollama from the Windows Start menu, or open a terminal and run:
  ```bash
  ollama serve
  ```
- If port `11434` is reported in use, verify if another instance is already running:
  ```powershell
  netstat -ano | findstr 11434
  ```

### 2. Missing Model Error: `Model 'MODEL_NAME' was not found in Ollama`
- **Cause**: The model configured in `.env` or selected in the UI has not been pulled yet.
- **Fix**: Run the pull command:
  ```bash
  ollama pull qwen3:1.7b
  ```

### 3. Generation Timeout on Laptops
- **Cause**: Large models (e.g., 14B or 70B) may take longer to load into RAM/VRAM on standard laptops without a dedicated GPU.
- **Fix**: 
  1. Use lightweight models like `qwen3:1.7b` (1.4 GB) or `llama3.2:3b`.
  2. Increase `OLLAMA_TIMEOUT=180` in `backend/.env`.

### 4. PowerShell `npm : File ... cannot be loaded because running scripts is disabled`
- **Cause**: Windows PowerShell default script execution policy restricts `.ps1` wrapper files.
- **Fix**: Run `npm.cmd` instead of `npm`, e.g.:
  ```powershell
  npm.cmd run dev
  npm.cmd run build
  ```

---

## 🔒 Security Considerations

Treating user API keys as high-security credentials is foundational to NoteTube:

1. **Local Mode**: When using Ollama, **zero API keys** are needed and zero data leaves your machine.
2. **No Persistent Storage**: Cloud API keys are **never stored** in `localStorage`, `sessionStorage`, cookies, or databases.
3. **Sanitized Logs**: Backend request logging masks and omits API keys entirely. No key values appear in terminal or log files.
4. **No Key Echoing**: API error responses never echo or expose the key.
5. **Clean Error Mapping**: Provider errors (such as `AuthenticationError`, `RateLimitError`, `NotFoundError`) are captured inside adapters and translated into clean user-friendly alerts.

---

## 🧪 Testing

### Backend Unit Tests & Ollama Verification
```bash
cd backend
python test_llm_providers.py
python test_transcript_service.py
python test_live_ollama.py
```

### Frontend Build Verification
```bash
cd frontend
npm.cmd run build
```

---

## 📄 License

MIT License. Feel free to use, modify, and build upon NoteTube!
