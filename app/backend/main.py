"""FastAPI application entry point with lifespan singletons and async I/O."""
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.logging import get_logger
from app.core.nltk_setup import ensure_nltk_resources  # noqa: F401 — side-effect import
from app.rag.generator import Generator
from app.rag.ingestion import IngestionPipeline
from app.rag.retriever import Retriever

logger = get_logger("supportbot.main")

# --- Rate limiter setup ---
limiter = Limiter(key_func=get_remote_address)


# --- Lifespan: initialize singletons on startup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create expensive singletons once on startup."""
    logger.info("startup_begin")
    try:
        app.state.ingestion_pipeline = IngestionPipeline()
        app.state.retriever = Retriever()
        app.state.generator = Generator()
        logger.info(
            "startup_complete",
            extra={"provider": settings.LLM_PROVIDER, "model": settings.LLM_MODEL},
        )
    except Exception as e:
        logger.error("startup_failed", extra={"error": str(e)})
        raise
    yield
    logger.info("shutdown_complete")


app = FastAPI(
    title="SupportBot QA - Conversational AI Testing Platform",
    lifespan=lifespan,
)

# --- Rate limiter middleware ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS: configurable via env ---
_allowed_origins = [
    o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials="*" not in _allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---
class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    query: str


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    answer: str
    sources: list[str]


# --- Auth dependency for /api/ingest ---
async def verify_ingest_api_key(
    x_api_key: str = Header(default=None, alias="X-API-Key"),
):
    """Validates the X-API-Key header for the /api/ingest endpoint.

    If INGEST_API_KEY is not set in the environment, the endpoint runs in
    dev mode (no auth) and logs a warning. In production, set INGEST_API_KEY
    to require all ingestion requests to carry a matching key.
    """
    expected = settings.INGEST_API_KEY
    if not expected:
        logger.warning(
            "ingest_auth_disabled",
            extra={"reason": "INGEST_API_KEY not set"},
        )
        return None
    if not x_api_key or x_api_key != expected:
        logger.warning("ingest_auth_failed")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


# --- Endpoints ---
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "SupportBot Backend"}


@app.post("/api/ingest")
@limiter.limit(settings.RATE_LIMIT_INGEST)
async def ingest_document(
    request: Request,
    file: UploadFile = File(...),
    _api_key: str = Depends(verify_ingest_api_key),
):
    """Upload and ingest documents into the knowledge base.

    Supported formats: .pdf, .txt, .md.
    Requires X-API-Key header when INGEST_API_KEY is set in the environment.
    """
    import shutil
    import uuid

    secure_filename = os.path.basename(file.filename)
    temp_file_path = f"temp_{uuid.uuid4()}_{secure_filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pipeline: IngestionPipeline = request.app.state.ingestion_pipeline
        chunks_count = await run_in_threadpool(pipeline.ingest, temp_file_path)

        logger.info(
            "ingest_success",
            extra={"source_filename": secure_filename, "chunks": chunks_count},
        )
        return {
            "filename": file.filename,
            "status": "success",
            "chunks_added": chunks_count,
        }
    except ValueError as e:
        logger.warning("ingest_value_error", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "ingest_failed",
            extra={"error": str(e), "source_filename": secure_filename},
        )
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def chat(request: Request, chat_request: ChatRequest):
    """Main chat endpoint utilizing the RAG pipeline.

    Processes a user query and returns an answer based on retrieved context.
    Retrieval and generation run in a threadpool to avoid blocking the
    async event loop (LangChain Qdrant/OpenAI clients are synchronous).
    """
    retriever: Retriever = request.app.state.retriever
    generator: Generator = request.app.state.generator
    try:
        context, sources = await run_in_threadpool(
            retriever.retrieve_context, chat_request.query
        )
        answer = await run_in_threadpool(
            generator.generate_answer, chat_request.query, context, sources
        )
        logger.info(
            "chat_success",
            extra={
                "has_context": bool(context),
                "sources_count": len(sources),
                "answer_length": len(answer),
            },
        )
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        logger.error("chat_failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
