from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import notes, providers, slides, video, modes, rag
from app.config import settings
from app.core.logging_config import setup_logging, request_id_var
from app.services.llm.ollama import check_ollama_startup
import logging
import uuid
import time

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    if settings.LLM_PROVIDER.lower() == "ollama":
        check = check_ollama_startup(
            base_url=settings.OLLAMA_BASE_URL,
            configured_model=settings.OLLAMA_MODEL
        )
        if check["status"] == "ok":
            logger.info(f"OLLAMA STARTUP | Status: Ready | Base URL: {check['base_url']} | Active Model: {check['configured_model']}")
        elif check["status"] == "model_missing":
            logger.warning(f"OLLAMA STARTUP | Model missing: '{check['configured_model']}'. Run: {check['suggested_command']}")
        else:
            logger.warning(f"OLLAMA STARTUP | Service offline. Run: {check['suggested_command']}")
    yield

app = FastAPI(
    title="NoteTube API",
    description="API for NoteTube - Dynamic AI YouTube Video Notes Generator",
    version="2.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    request_id_var.set(req_id)
    
    # Only log API requests, skip health checks etc. to avoid spam
    is_api = any(request.url.path.startswith(p) for p in [
        "/api/notes", "/api/providers", "/api/slides", "/api/video", "/api/modes", "/api/rag"
    ])
    if is_api:
        logger.info(f"PIPELINE | Received API request | path={request.url.path} method={request.method}")
    
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        if is_api:
            logger.info(f"PIPELINE | Request completed | path={request.url.path} status={response.status_code} duration={process_time:.2f}s")
        return response
    except Exception as e:
        process_time = time.perf_counter() - start_time
        logger.exception(f"PIPELINE | ERROR | Unhandled exception during request | path={request.url.path} duration={process_time:.2f}s")
        raise

# CORS configuration
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys([o for o in allowed_origins if o])),
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.onrender\.com)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(slides.router, prefix="/api/slides", tags=["slides"])
app.include_router(video.router, prefix="/api/video", tags=["video"])
app.include_router(modes.router, prefix="/api/modes", tags=["modes"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])


@app.api_route("/health", methods=["GET", "HEAD"], tags=["health"])
async def health_check():
    """Health check endpoint returning service status."""
    return {"status": "healthy", "service": "NoteTube"}

@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["health"])
async def api_health_check():
    """Health check endpoint under API prefix."""
    return {"status": "healthy", "service": "NoteTube"}

@app.api_route("/", methods=["GET", "HEAD"], tags=["health"])
async def root():
    """Root endpoint for status check."""
    return {"status": "healthy", "service": "NoteTube", "message": "NoteTube API is running"}

@app.get("/api/ollama/status", tags=["ollama"])
async def ollama_status():
    """
    Check Ollama connection, service status, installed models, and active model availability.
    """
    return check_ollama_startup(
        base_url=settings.OLLAMA_BASE_URL,
        configured_model=settings.OLLAMA_MODEL
    )
