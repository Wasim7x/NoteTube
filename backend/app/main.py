from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import notes
from app.config import settings
from app.core.logging_config import setup_logging, request_id_var
import logging
import uuid
import time

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NoteTube API",
    description="API for NoteTube - AI YouTube Video Notes Generator",
    version="1.0.0"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    request_id_var.set(req_id)
    
    # Only log API requests, skip health checks etc. to avoid spam
    if request.url.path.startswith("/api/notes"):
        logger.info(f"PIPELINE | Received API request | path={request.url.path}")
    
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        if request.url.path.startswith("/api/notes"):
            logger.info(f"PIPELINE | Request completed | path={request.url.path} status={response.status_code} duration={process_time:.2f}s")
        return response
    except Exception as e:
        process_time = time.perf_counter() - start_time
        logger.exception(f"PIPELINE | ERROR | Unhandled exception during request | path={request.url.path} duration={process_time:.2f}s")
        raise

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])

@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
