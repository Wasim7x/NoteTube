# NoteTube

> Dynamic AI YouTube Study Assistant, Visual Slide Generator, and Grounded Transcript RAG Engine.

[![Python](https://img.shields.io/badge/Python-3.11.9-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-8.2-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.3-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Application Architecture](#application-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Local Setup](#installation-and-local-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Testing and Code Quality](#testing-and-code-quality)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Limitations and Roadmap](#limitations-and-roadmap)
- [Contributing](#contributing)
- [License and Author](#license-and-author)

---

## Overview

Long-form video content—including technical tutorials, conference lectures, full-length courses, and podcasts—is packed with critical knowledge, but extracting actionable notes from hours of video is tedious and inefficient. Existing summarization tools suffer from major drawbacks:
1. **Cloud Lock-in & Privacy Risks:** Most tools require transmitting proprietary content and credit card-backed API tokens to third-party cloud servers.
2. **Static Server Configuration:** Traditional web applications hardcode a single model provider in server-side configuration files, forcing developers to restart services or edit `.env` files whenever they switch models.
3. **Loss of Visual Context:** Standard tools process only text transcripts, discarding the slide diagrams, code listings, and whiteboard visual illustrations essential for deep technical comprehension.
4. **Hallucination in Q&A:** Generic chat interfaces lack deterministic grounding against the actual video timeline, producing answers without verifiable timestamps.

### How NoteTube Solves This

**NoteTube** is a high-performance, full-stack AI engineering platform that converts any YouTube URL into structured, publication-ready study notes, synchronized 16:9 presentation slide decks, and a grounded transcript chatbot.

NoteTube is built around three core engineering principles:

- **Local-First & Zero Cloud API Key Dependency:** NoteTube runs 100% locally and privately using **Ollama** on consumer hardware. No external subscriptions, keys, or data egress are required.
- **Dynamic Runtime Provider Switching:** Switch seamlessly on-the-fly between local Ollama inference and cloud LLM providers (Google Gemini, OpenAI, Anthropic Claude, Groq LPU, and OpenRouter) directly from the browser interface.
- **Multi-Modal Synthesis:** Beyond text summarization, NoteTube extracts representative presentation slides at precise chapter boundaries via computer vision (`OpenCV`), bundles them into native PowerPoint presentations (`.pptx`), and provides an interactive Retrieval-Augmented Generation (RAG) assistant with timestamp citations.

---

## Key Features

### 1. Multi-Provider & Local-First AI Engine
- **Ollama (100% Local & Private):** Execute open-source models (`qwen3:1.7b`, `qwen3.5:latest`, `llama3.2:3b`, `mistral:7b`) offline on your workstation.
- **Leading Cloud LLM Providers:** Integrated support for Google Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`), OpenAI (`gpt-4o-mini`, `gpt-4o`, `o3-mini`), Anthropic Claude (`claude-3-7-sonnet-latest`, `claude-3-5-sonnet-latest`), Groq LPU (`openai/gpt-oss-20b`, `llama-3.3-70b-versatile`), and OpenRouter (`deepseek/deepseek-chat`, `deepseek/deepseek-r1`).
- **Custom Model IDs:** Enter any provider-supported model identifier in addition to built-in presets.
- **Credential Security:** Cloud API keys are stored solely in tab-scoped browser memory (`sessionStorage`). They are never persisted to databases, server disks, or browser `localStorage`, and backend loggers actively mask credentials.
- **Live Connection Validator:** Test provider connectivity and model availability in real time before processing videos.

### 2. Multi-Stage Video Ingestion & Chapter Segmentation
- **Robust Transcript Pipeline:** Language-agnostic transcript extraction with automatic fallback cascades (`youtube-transcript-api` and `yt-dlp`). Supports manual and auto-generated captions across languages.
- **Transcript-Free Fallback:** When a video has no available transcript, NoteTube synthesizes fallback notes using video metadata, descriptions, and detected chapter outlines.
- **Intelligent Chapter Detection:** Automatically ingests official YouTube video chapters; if absent, an LLM-driven semantic segmenter splits the video into coherent, timestamped topics.

### 3. Specialized Processing Modes
NoteTube separates workflows into modular, on-demand execution modes:
- **Mode 1: Quick Summary:** Ultra-fast transcript processing that extracts executive summaries, core concepts, and key takeaways without downloading video files.
- **Mode 2: Detailed Notes:** Pedagogical study notes organized into structured chapter sections, complete with technical definitions, practical examples, and core takeaways.
- **Mode 3: Chapter-End Slides & PPTX Generation:**
  - Employs OpenCV to extract a crisp video frame exactly 5 seconds before each chapter boundary (`extraction_timestamp = max(chapter_start_time, chapter_end_time - 5)`).
  - Preserves 16:9 widescreen presentation aspect ratios with proportional scaling.
  - Automatically compiles slide frames and chapter titles into a downloadable PowerPoint deck (`.pptx`).
  - Provides in-browser full-screen modal previews with direct jump-to-chapter timestamps.
- **Mode 4: Advanced Unique Slides:** Perceptual hashing and scene-change detection pipeline *(documented in development)*.
- **Mode 5: Complete AI Notes:** Full end-to-end pipeline uniting video overview, interactive table of contents, in-depth chapter notes, slide gallery, and a final quick-revision recap.

### 4. Grounded Video RAG Chatbot
- **Interactive Chat Drawer:** Ask natural-language questions about any loaded video.
- **Deterministic Dense Embedder:** Utilizes an integrated 384-dimensional sublinear TF-IDF and n-gram local embedder with L2 normalization and cosine similarity. Requires zero external embedding API keys and runs with sub-5ms search latencies.
- **Optional Cloud Embeddings:** Seamlessly cascades to Gemini (`text-embedding-004`), OpenAI (`text-embedding-3-small`), or Ollama (`/api/embed`) when available.
- **Verifiable Citations:** Responses cite exact timestamps and chapter headings, allowing users to verify claims against the original video.

### 5. Export and Developer Utilities
- **One-Click Exports:** Export generated notes as formatted Markdown (`.md`), print/download formatted PDF documents via `html2pdf.js`, or copy clean text to the clipboard.
- **Server-Sent Events (SSE):** Real-time progressive streaming endpoint (`/api/notes/generate-stream`) for streaming notes as chapters finish processing.
- **Preflight Diagnostics:** Built-in Python CLI diagnostic script (`check_ollama.py`) to verify Ollama status, network connectivity, and model weights before launching the application.

---

## Application Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (React 19 + TypeScript + Vite)"]
        UI_Config["Page 1: Model Configuration & Live Validation"]
        UI_Dash["Page 2: Video Dashboard & Mode Selector"]
        UI_Results["Page 3: Results Viewer & Markdown Renderer"]
        UI_Chat["RAG Video Chatbot Drawer"]
        UI_Slides["Chapter Slides Gallery & Modal"]
    end

    subgraph API["FastAPI Application Backend (Port 8000)"]
        Router_Health["/health & /api/health"]
        Router_Providers["/api/providers & /validate"]
        Router_Video["/api/video/load & /{video_id}"]
        Router_Modes["/api/modes/quick-summary & detailed-notes"]
        Router_Notes["/api/notes/generate & /generate-stream (SSE)"]
        Router_Slides["/api/slides/extract & /download-ppt"]
        Router_RAG["/api/rag/ask & /status/{video_id}"]
    end

    subgraph Ingestion["Video Ingestion & Processing Pipeline"]
        YT_Service["YouTube Metadata (yt-dlp)"]
        Trans_Service["Transcript Service (youtube-transcript-api)"]
        CV_Engine["OpenCV Headless Frame Grabber"]
        PPT_Engine["python-pptx 16:9 Deck Builder"]
    end

    subgraph LLM_Layer["LLM Abstraction & Provider Registry"]
        Prov_Ollama["Ollama (Local REST :11434)"]
        Prov_Gemini["Google Gemini (google-genai SDK)"]
        Prov_OpenAI["OpenAI (openai SDK)"]
        Prov_Anthropic["Anthropic Claude (anthropic SDK)"]
        Prov_Groq["Groq (groq SDK)"]
        Prov_OpenRouter["OpenRouter (HTTP Client)"]
    end

    subgraph Storage["Persistence & Local Cache"]
        Disk_Slides["backend/data/slides/{video_id}/*.jpg & .pptx"]
        Disk_RAG["backend/data/rag/{video_id}/index.json"]
        Session_Store["Browser sessionStorage (API Keys & Session State)"]
    end

    %% Interactions
    UI_Config -->|POST /api/providers/validate| Router_Providers
    UI_Dash -->|POST /api/video/load| Router_Video
    Router_Video --> YT_Service
    Router_Video --> Trans_Service

    UI_Dash -->|POST /api/modes/*| Router_Modes
    Router_Modes --> LLM_Layer

    UI_Dash -->|POST /api/slides/extract| Router_Slides
    Router_Slides --> CV_Engine
    CV_Engine --> Disk_Slides
    Router_Slides --> PPT_Engine
    PPT_Engine --> Disk_Slides

    UI_Chat -->|POST /api/rag/ask| Router_RAG
    Router_RAG --> Disk_RAG
    Router_RAG --> LLM_Layer

    Router_Providers --> LLM_Layer
    Router_Notes --> LLM_Layer

    UI_Results -->|GET /api/slides/{id}/download-ppt| Router_Slides
```

### Component Flow

1. **Model Handshake:** The frontend initiates a connection test against `/api/providers/validate`. For Ollama, the backend queries `http://localhost:11434/api/tags`. For cloud providers, a minimal test prompt verifies credentials.
2. **Video Preload:** The user submits a YouTube URL to `/api/video/load`. The backend extracts video metadata (title, duration, author, chapters) and transcript segments, caching them in memory for downstream workflows.
3. **Synthesis Pipeline:** When a mode is triggered, `SummarizationService` formats transcript chunks against structured prompt templates and streams them to the selected LLM provider adapter.
4. **Slide Extraction:** If slide extraction is requested, `SlideService` calculates target timestamps (`max(start, end - 5)`), executes stream-seeking with `yt-dlp` and `OpenCV`, saves JPEG frames to `backend/data/slides/`, and generates a styled 16:9 `.pptx` presentation.
5. **RAG Vector Search:** The RAG engine chunks transcript segments into 160-word overlapping windows, vectors them via the deterministic local TF-IDF embedder, and performs top-$k$ cosine similarity retrieval to answer user queries with timestamp citations.

---

## Technology Stack

### Backend
- **Framework:** FastAPI (`>=0.115.0`) with Uvicorn ASGI server (`>=0.30.0`).
- **Data Validation & Settings:** Pydantic v2 (`>=2.10.0`), Pydantic Settings (`>=2.6.0`).
- **HTTP Clients:** HTTPX (`>=0.27.0`), Requests (`>=2.32.0`).
- **AI & LLM SDKs:**
  - `google-genai` (`>=0.3.0`)
  - `openai` (`>=1.50.0`)
  - `anthropic` (`>=0.40.0`)
  - `groq` (`>=0.11.0`)
  - Ollama REST API Client
- **Video & Media Processing:**
  - `yt-dlp` (`>=2024.8.0`)
  - `youtube-transcript-api` (`>=0.6.2`)
  - `opencv-python-headless` (`>=4.8.0`)
  - `python-pptx` (`>=1.0.0`)
  - `Pillow` (`>=10.0.0`)
  - `defusedxml` (`>=0.7.1`)
- **Mathematical & Vector Computation:** NumPy (`>=1.26.0`).

### Frontend
- **Framework & Build Tool:** React 19 (`^19.2.8`), TypeScript (`~6.0.2`), Vite 8 (`^8.2.2`).
- **Routing:** React Router DOM v7 (`^7.18.3`).
- **Styling:** Tailwind CSS v4 (`^4.3.3`), PostCSS (`^8.5.26`), Lucide React Icons (`^1.38.0`).
- **Markdown & Code Rendering:** `react-markdown` (`^10.1.0`), `remark-gfm` (`^4.0.1`), `react-syntax-highlighter` (`^16.1.1`).
- **Document Export:** `html2pdf.js` (`^0.14.0`).
- **Networking:** Axios (`^1.20.0`), Fetch API (Server-Sent Events streaming).
- **Code Quality:** Oxlint (`^1.79.0`).

---

## Project Structure

```text
NoteTube/
├── render.yaml                   # Infrastructure-as-Code Render Blueprint specification
├── README.md                     # Project documentation
├── backend/
│   ├── runtime.txt               # Pinned Python version (python-3.11.9)
│   ├── requirements.txt          # Backend dependencies
│   ├── .env.example              # Sample environment configuration template
│   ├── check_ollama.py           # Preflight diagnostic checker for local Ollama
│   ├── test_all_scenarios.py     # Integration test suite covering chapter scenarios
│   ├── test_chapter_notes.py     # Chapter segmentation & notes unit tests
│   ├── test_new_features.py      # Tests for RAG, connection validator, and endpoints
│   ├── test_slide_service.py     # Tests for OpenCV frame calculations & PPTX export
│   ├── test_transcript_service.py# Tests for transcript extraction & fallback cascades
│   ├── test_live_ollama.py       # Live pipeline validation against active Ollama daemon
│   ├── data/                     # Generated runtime artifacts (gitignored)
│   │   ├── rag/                  # Persistent TF-IDF vector indexes per video ID
│   │   └── slides/               # Extracted JPEG slide frames and .pptx presentations
│   └── app/
│       ├── main.py               # FastAPI application entry point, CORS, routers
│       ├── config.py             # Pydantic Settings and environment configuration
│       ├── core/
│       │   └── logging_config.py # Structured logging with correlation IDs
│       ├── models/
│       │   ├── schemas.py        # Pydantic request/response data contracts
│       │   └── transcript.py     # Normalized transcript domain models
│       ├── prompts/
│       │   └── notes_prompt.py   # System and user prompts for notes and RAG QA
│       ├── services/
│       │   ├── chapter_service.py       # Official & AI-detected chapter boundary segmentation
│       │   ├── notes_service.py         # End-to-end notes generation orchestrator
│       │   ├── rag_service.py           # Local TF-IDF embedder and cosine retriever
│       │   ├── slide_service.py         # OpenCV frame extraction and python-pptx generation
│       │   ├── summarization_service.py # Summarization engine for quick/detailed modes
│       │   ├── transcript_service.py    # Multi-language transcript retrieval & fallback
│       │   ├── video_service.py         # Video metadata loader & memory cache
│       │   ├── youtube_service.py       # yt-dlp metadata extraction utilities
│       │   └── llm/
│       │       ├── base.py              # Abstract base class for LLM providers
│       │       ├── factory.py           # Dynamic provider instantiation factory
│       │       ├── registry.py          # Provider metadata, models, and presets
│       │       ├── connection_test.py   # Live connectivity testing implementation
│       │       ├── ollama.py            # Ollama local inference adapter
│       │       ├── gemini.py            # Google Gemini provider adapter
│       │       ├── openai.py            # OpenAI GPT provider adapter
│       │       ├── anthropic.py         # Anthropic Claude provider adapter
│       │       ├── groq.py              # Groq LPU provider adapter
│       │       └── openrouter.py        # OpenRouter provider adapter
│       └── api/
│           └── routes/
│               ├── modes.py             # Quick Summary & Detailed Notes routes
│               ├── notes.py             # Synchronous & SSE notes generation routes
│               ├── providers.py         # Provider listing & validation routes
│               ├── rag.py               # Grounded video Q&A and index status routes
│               ├── slides.py            # Frame extraction & PPTX download routes
│               └── video.py             # Video metadata loading and caching routes
└── frontend/
    ├── package.json              # Frontend scripts and npm dependencies
    ├── vite.config.ts            # Vite configuration
    ├── tsconfig.json             # TypeScript configuration
    ├── tailwind.config.js        # Tailwind CSS configuration
    ├── .env                      # Default frontend environment (VITE_API_URL)
    ├── .env.development          # Development frontend environment
    ├── src/
    │   ├── main.tsx              # React application DOM mount
    │   ├── App.tsx               # Route declarations, health monitoring, session state
    │   ├── index.css             # Tailwind base styles
    │   ├── types/
    │   │   └── index.ts          # TypeScript type definitions matching backend schemas
    │   ├── services/
    │   │   ├── api.ts            # Axios API client and Server-Sent Events stream consumer
    │   │   └── jobStorage.ts     # Client-side session and job caching
    │   └── components/
    │       ├── Header.tsx            # Header with breadcrumbs and live backend health indicator
    │       ├── ModelConfigPage.tsx   # Page 1: Provider selection & live validation
    │       ├── DashboardPage.tsx     # Page 2: YouTube URL ingestion & Mode Selector
    │       ├── ResultsPage.tsx       # Page 3: Output viewer, tab navigation, slide gallery
    │       ├── ModeSelector.tsx      # 5-card processing mode selection component
    │       ├── NotesViewer.tsx       # Markdown notes renderer with syntax highlighting
    │       ├── QuickSummaryView.tsx  # Executive summary & key takeaway viewer
    │       ├── DetailedNotesView.tsx # Chapter-by-chapter deep study notes viewer
    │       ├── SlidesGallery.tsx     # Chapter slide thumbnail grid and download trigger
    │       ├── SlidePreviewModal.tsx # Fullscreen slide viewer with timestamp seek links
    │       ├── ChatbotDrawer.tsx     # Interactive slide-out RAG Q&A chat drawer
    │       ├── Actions.tsx           # Export buttons (Markdown, PDF, Clipboard)
    │       ├── UrlInput.tsx          # YouTube URL submission input with validation
    │       ├── VideoLoader.tsx       # Video metadata display card
    │       └── LoadingState.tsx      # Multi-step animated progress loader
```

---

## Prerequisites

Ensure the following tools are installed on your workstation:

| Requirement | Minimum Version | Verified Version | Purpose |
|---|---|---|---|
| **Python** | `3.11.0+` | `3.11.9` / `3.14.x` | Backend runtime |
| **Node.js** | `18.0.0+` | `20.x` / `22.x` | Frontend package execution |
| **npm** | `9.0.0+` | `10.x+` | Frontend package manager |
| **Ollama** *(Optional)* | Latest | `0.5.x+` | 100% offline local LLM inference |
| **Git** | Latest | `2.x+` | Source control |

---

## Installation and Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Wasim7x/NoteTube.git
cd NoteTube
```

### 2. Backend Setup

#### On Windows (PowerShell):
```powershell
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
Copy-Item .env.example .env
```

#### On Linux / macOS (Bash):
```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Frontend Setup

#### On Windows (PowerShell):
```powershell
# Open a second terminal and navigate to frontend
cd frontend

# Install dependencies
# (Use npm.cmd if PowerShell execution policy restricts npm.ps1)
npm.cmd install
```

#### On Linux / macOS (Bash):
```bash
cd frontend
npm install
```

### 4. (Optional) Local Ollama AI Setup
If you want to run completely locally without cloud API keys:
1. Download Ollama from [ollama.com](https://ollama.com/download).
2. Start the Ollama background daemon:
   ```bash
   ollama serve
   ```
3. Pull the recommended lightweight local model:
   ```bash
   ollama pull qwen3:1.7b
   ```
4. Verify the setup with NoteTube's preflight checker:
   ```bash
   cd backend
   python check_ollama.py
   ```

---

## Environment Configuration

### Backend Configuration (`backend/.env`)

| Variable | Purpose | Required | Default |
|---|---|---|---|
| `LLM_PROVIDER` | Default LLM provider on backend startup (`ollama`, `gemini`, `openai`, `anthropic`, `groq`, `openrouter`) | Yes | `ollama` |
| `OLLAMA_BASE_URL` | Base HTTP endpoint where the local Ollama service is listening | Yes | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default model tag to query on Ollama | Yes | `qwen3:1.7b` |
| `OLLAMA_TIMEOUT` | Request timeout in seconds for local model inference | Yes | `120.0` |
| `FRONTEND_URL` | Allowed origin URL for Cross-Origin Resource Sharing (CORS) | Yes | `http://localhost:5173` |
| `PORT` | Local port on which the FastAPI Uvicorn server binds | Yes | `8000` |
| `HOST` | Network interface binding | Yes | `0.0.0.0` |
| `GEMINI_API_KEY` | *(Optional)* Cloud API key fallback for Google Gemini | No | Not specified |
| `GROQ_API_KEY` | *(Optional)* Cloud API key fallback for Groq LPUs | No | Not specified |
| `OPENAI_API_KEY` | *(Optional)* Cloud API key fallback for OpenAI | No | Not specified |
| `ANTHROPIC_API_KEY` | *(Optional)* Cloud API key fallback for Anthropic Claude | No | Not specified |
| `OPENROUTER_API_KEY` | *(Optional)* Cloud API key fallback for OpenRouter | No | Not specified |

> **Security Note:** Cloud API keys can be provided directly via the frontend UI at runtime. You do not need to populate cloud keys in your server `.env` file unless you want fixed backend defaults.

### Frontend Configuration (`frontend/.env`)

| Variable | Purpose | Required | Default |
|---|---|---|---|
| `VITE_API_URL` | Base URL of the NoteTube FastAPI backend API | Yes | `http://127.0.0.1:8000/api` |

---

## Running the Application

### 1. Start Ollama (If Using Local Mode)
Ensure Ollama is running in the background:
```bash
ollama serve
```

### 2. Start the Backend API Server (Terminal 1)
```powershell
cd backend
# With virtual environment activated:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API Base:** `http://localhost:8000`
- **Interactive Swagger Documentation:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`
- **Health Check Endpoint:** `http://localhost:8000/health`

### 3. Start the Frontend Dev Server (Terminal 2)
```powershell
cd frontend
# On Windows PowerShell:
npm.cmd run dev

# On Linux / macOS:
npm run dev
```
- **Frontend User Interface:** `http://localhost:5173`

---

## Usage Guide

### Complete End-to-End Workflow

```text
Step 1: LLM Configuration (http://localhost:5173)
  ├── Select Provider (Ollama Local, Gemini, OpenAI, Claude, Groq, OpenRouter)
  ├── Pick Preset Model (or input Custom Model name)
  ├── Enter API Key (if using Cloud provider)
  └── Click "Test Connection & Continue" (Live validation ensures zero failed runs)
        ↓
Step 2: Video Dashboard (/video)
  ├── Paste any YouTube URL (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)
  ├── NoteTube fetches video metadata, duration, channel, and transcript
  └── Select Processing Mode:
        • [1] Quick Summary (Instant transcript digest)
        • [2] Detailed Notes (Pedagogical chapter notes)
        • [3] Chapter-End Slides & PPTX (OpenCV frame capture + PowerPoint)
        • [5] Complete AI Notes (All-in-one comprehensive pipeline)
        ↓
Step 3: Results Workspace (/results/:jobId)
  ├── Tab 1: Structured Notes Viewer (Markdown, code syntax highlighting, copy/export)
  ├── Tab 2: Visual Chapter Slides Gallery (Fullscreen modal + One-Click "Download PPTX")
  └── Slide-out Drawer: Interactive RAG Chatbot (Query the video with timestamped citations)
```

---

## API Reference

The NoteTube FastAPI backend exposes a structured REST API documented interactively at `/docs`.

### Core Endpoints

#### 1. System Health
- **`GET /health`** or **`GET /api/health`**
  - Returns service status: `{"status": "healthy", "service": "NoteTube"}`.
- **`GET /api/ollama/status`**
  - Returns detailed local Ollama diagnostics, including service availability and installed models:
  ```json
  {
    "status": "ok",
    "service_running": true,
    "cli_installed": true,
    "installed_models": ["qwen3:1.7b", "qwen3.5:latest"],
    "configured_model": "qwen3:1.7b",
    "model_exists": true
  }
  ```

#### 2. Provider Management
- **`GET /api/providers`**
  - Lists all 6 supported LLM providers, their descriptions, help URLs, and model presets.
- **`POST /api/providers/validate`**
  - Validates provider credentials and tests live connectivity.
  - **Request Body:**
    ```json
    {
      "provider": "ollama",
      "model": "qwen3:1.7b",
      "api_key": ""
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "provider": "ollama",
      "model": "qwen3:1.7b",
      "message": "Successfully connected to Ollama service. Model 'qwen3:1.7b' is ready."
    }
    ```

#### 3. Video Loading & Caching
- **`POST /api/video/load`**
  - Validates YouTube URL, extracts metadata and transcript, and caches the result for downstream modes.
  - **Request Body:**
    ```json
    {
      "youtube_url": "https://www.youtube.com/watch?v=SahaDGzN_Bk"
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "video_id": "SahaDGzN_Bk",
      "video": {
        "id": "SahaDGzN_Bk",
        "title": "Introduction to Algorithms",
        "thumbnail": "https://i.ytimg.com/vi/SahaDGzN_Bk/maxresdefault.jpg",
        "duration": 3600,
        "channel": "MIT OpenCourseWare"
      },
      "transcript_available": true,
      "transcript_language": "English",
      "total_chapters": 5,
      "chapters": [
        {
          "title": "Course Overview",
          "start_time": 0.0,
          "end_time": 420.0,
          "timestamp_str": "00:00"
        }
      ]
    }
    ```

#### 4. Specialized Note Modes
- **`POST /api/modes/quick-summary`**
  - Generates an executive summary with key takeaways and core concepts from the cached transcript.
- **`POST /api/modes/detailed-notes`**
  - Generates structured, chapter-by-chapter pedagogical study notes.
- **`POST /api/notes/generate`**
  - Executes the complete monolithic notes generation pipeline.
- **`POST /api/notes/generate-stream`**
  - Server-Sent Events (SSE) endpoint emitting progressive chapter generation events (`data: {"type": "chapter", ...}`).

#### 5. Computer Vision Slides & PowerPoint
- **`POST /api/slides/extract`**
  - Extracts representative chapter frames using OpenCV and builds a 16:9 `.pptx` presentation.
  - **Request Body:**
    ```json
    {
      "video_id": "SahaDGzN_Bk",
      "youtube_url": "https://www.youtube.com/watch?v=SahaDGzN_Bk"
    }
    ```
- **`GET /api/slides/{video_id}`**
  - Returns metadata and image URLs for all extracted chapter slides.
- **`GET /api/slides/{video_id}/images/{chapter_id}`**
  - Serves the extracted JPEG slide image.
- **`GET /api/slides/{video_id}/download-ppt`**
  - Streams the generated `.pptx` presentation file with sanitized attachment headers.

#### 6. Retrieval-Augmented Generation (RAG)
- **`POST /api/rag/ask`**
  - Answers a user question grounded in the video transcript.
  - **Request Body:**
    ```json
    {
      "video_id": "SahaDGzN_Bk",
      "query": "What is the time complexity of merge sort explained in this lecture?",
      "provider": "ollama",
      "model": "qwen3:1.7b"
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "video_id": "SahaDGzN_Bk",
      "query": "What is the time complexity of merge sort explained in this lecture?",
      "answer": "Merge sort runs in O(n log n) time in all cases because it divides the array into two halves recursively and performs a linear merge operation [14:20 – 16:45].",
      "grounded": true,
      "sources": [
        {
          "chunk_id": "SahaDGzN_Bk_c_3",
          "timestamp_str": "14:20 – 16:45",
          "start_time": 860.0,
          "end_time": 1005.0,
          "chapter_title": "Divide and Conquer",
          "text": "Merge sort divides the problem into two subproblems of size n/2...",
          "score": 0.884
        }
      ]
    }
    ```
- **`GET /api/rag/status/{video_id}`**
  - Checks if a persistent vector index exists for the specified video ID.

---

## Testing and Code Quality

### Backend Unit & Integration Tests

The backend includes a comprehensive automated test suite with **50 unit and integration tests** covering all application scenarios, mocking external APIs to guarantee fast, deterministic runs.

```bash
cd backend

# Execute all verified test suites
python -m pytest test_all_scenarios.py test_slide_service.py test_chapter_notes.py test_new_features.py test_transcript_service.py -v
```

#### Test Suite Breakdown:
- `test_all_scenarios.py` (7 tests): Official chapters, videos lacking chapters, long videos with 8+ chapters, non-English transcripts, transcript-missing fallbacks, and Ollama connection recovery.
- `test_slide_service.py` (16 tests): Timestamp computation (`max(start, end - 5)`), short chapter boundary clamping, synthetic video frame extraction, widescreen 16:9 `.pptx` structure validation, and path traversal security guards.
- `test_chapter_notes.py` (6 tests): Chapter detection normalization, LLM prompt formatting, and Server-Sent Events (SSE) streaming verification.
- `test_new_features.py` (13 tests): Local TF-IDF embedder cosine similarity, connection testing validator, video caching, quick summary mode, and RAG grounding.
- `test_transcript_service.py` (8 tests): Language selection priority, auto-generated subtitle parsing, and graceful fallbacks.

### Frontend Quality Checks

```bash
cd frontend

# Verify TypeScript compilation and production bundle build
npm.cmd run build

# Run fast Oxlint code quality checks
npm.cmd run lint
```

---

## Deployment

NoteTube is fully prepared for multi-service deployment via the included [`render.yaml`](render.yaml) blueprint.

### Deploying to Render via Blueprint

1. Fork or push NoteTube to your GitHub account.
2. In the [Render Dashboard](https://dashboard.render.com/), select **New > Blueprint**.
3. Connect your `NoteTube` repository. Render automatically reads `render.yaml` and provisions:
   - **Backend Web Service (`notetube-backend`):**
     - Runtime: Python `3.11.9`
     - Root Directory: `backend`
     - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Health Check Path: `/health`
   - **Frontend Static Site (`notetube-frontend`):**
     - Runtime: Static Site
     - Root Directory: `frontend`
     - Build Command: `npm install && npm run build`
     - Publish Directory: `dist`
     - Route Rewrites: `/*` -> `/index.html` (React Router SPA)
     - Environment Variable: `VITE_API_URL=https://notetube-backend.onrender.com/api`

### Production Considerations
- **CORS Configuration:** In `backend/app/main.py`, CORS automatically permits requests matching `r"^https?://(localhost|127\.0\.0\.1|.*\.onrender\.com)(:[0-9]+)?$"`. For custom domain deployments, update `FRONTEND_URL` in your backend environment variables.
- **Media Storage:** Extracted slides and PowerPoint files are stored in `backend/data/slides/`. For persistent multi-instance deployments, attach a Render Persistent Disk or configure cloud object storage (e.g., AWS S3).
- **Headless Video Processing:** NoteTube uses `opencv-python-headless` in `requirements.txt`, ensuring OpenCV runs reliably in containerized and cloud Linux environments without requiring X11 display libraries.

---

## Troubleshooting

### 1. Ollama Connection Refused (`http://localhost:11434`)
- **Symptom:** UI displays `"Could not connect to Ollama service at http://localhost:11434"`.
- **Cause:** The Ollama background daemon is not running.
- **Solution:** Open your terminal and run `ollama serve`. If port 11434 is occupied on Windows, inspect running processes using `netstat -ano | findstr 11434`.

### 2. Model Not Found in Ollama
- **Symptom:** Backend returns `"Model 'qwen3:1.7b' was not found in Ollama"`.
- **Cause:** The specified model weights have not been downloaded to your machine.
- **Solution:** Run `ollama pull qwen3:1.7b` in your terminal. You can also run `python backend/check_ollama.py` to confirm model availability.

### 3. Windows PowerShell Script Execution Policy
- **Symptom:** `npm : File C:\...\npm.ps1 cannot be loaded because running scripts is disabled on this system`.
- **Cause:** Default PowerShell execution policy restricts unassigned `.ps1` execution.
- **Solution:** Either invoke `npm.cmd` (e.g., `npm.cmd run dev`), or update your session execution policy:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  ```

### 4. Videos Without Transcripts
- **Symptom:** Video does not have subtitles, or YouTube blocks automated caption extraction for a specific IP.
- **Handling:** NoteTube automatically activates its fallback synthesis pipeline, summarizing the video from its title, author, description, and chapter landmarks.

### 5. Port Conflicts
- If port `8000` is already in use, launch the backend on an alternate port:
  ```bash
  python -m uvicorn app.main:app --port 8080 --reload
  ```
  Then set `VITE_API_URL=http://localhost:8080/api` in `frontend/.env`.

---

## Limitations and Roadmap

### Current Limitations
- **Caption Availability:** Ingestion relies on YouTube transcripts or descriptions. Videos without speech or written descriptions will have limited summary detail.
- **Single-Node Slide Storage:** Extracted slide images and generated `.pptx` decks are cached locally in the filesystem (`backend/data/slides/`).
- **Mode 4 Status:** The Advanced Unique Slides mode using perceptual frame deduplication is currently marked as *Coming Soon* in the UI.

### Planned Roadmap
- [ ] **Whisper Audio Transcriber:** Integrate local `faster-whisper` for offline speech-to-text fallback when YouTube captions are unavailable.
- [ ] **Perceptual Slide Deduplication:** Implement structural similarity indexing (SSIM) and perceptual hashing (`pHash`) to extract unique presentation slides regardless of chapter markers.
- [ ] **Multi-Language Translation:** Translate synthesized study notes into multiple target languages on demand.
- [ ] **S3 / Cloud Storage Adapter:** Add optional S3-compatible cloud storage for PowerPoint decks and slide images.

---

## Contributing

Contributions to NoteTube are welcome! Please follow these steps:

1. **Fork the Repository:** Create your own fork of `Wasim7x/NoteTube`.
2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Write Tests & Implement:** Add tests covering your changes in `backend/` or `frontend/`.
4. **Validate Code Quality:**
   ```bash
   # Run backend tests
   cd backend && python -m pytest test_all_scenarios.py test_slide_service.py test_new_features.py -v

   # Run frontend build and linter
   cd ../frontend && npm.cmd run build && npm.cmd run lint
   ```
5. **Submit a Pull Request:** Open a PR against `main` with a clear explanation of your changes and test results.

---

## License and Author

- **Author:** Wasim ([@Wasim7x](https://github.com/Wasim7x))
- **Repository:** [https://github.com/Wasim7x/NoteTube](https://github.com/Wasim7x/NoteTube)
- **License:** Distributed under the [MIT License](https://opensource.org/licenses/MIT).
