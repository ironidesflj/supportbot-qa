# Architecture Overview

## High-Level Design

The architecture follows a Modular Monolith pattern, ensuring separation of concerns while keeping deployment simple via Docker Compose or managed PaaS (Render + Vercel).

### Components

- **API Layer (`app/backend`)**: Exposes REST endpoints for chat and ingestion. Handles HTTP concerns, validation, authentication, and rate limiting. Uses FastAPI lifespan to instantiate expensive singletons (Retriever, Generator, IngestionPipeline) once on startup.

- **RAG Domain (`app/rag`)**: Contains the core business logic.
  - `DirectGeminiEmbeddings` (`embeddings.py`): Custom LangChain `Embeddings` implementation that calls `google.generativeai.embed_content()` directly, bypassing the buggy `langchain-google-genai` wrapper. Handles batching (5 texts) and retry with exponential backoff.
  - `thresholds.py`: Per-model similarity threshold lookup table. Different embedding models have different score distributions; a single hardcoded threshold was causing false positives/negatives.
  - `IngestionPipeline`: Parses files (PDF, TXT, MD), chunks text (600 chars, 100 overlap), embeds via DirectGeminiEmbeddings, and upserts to Qdrant with explicit payload (page_content, source_file, chunk_index).
  - `Retriever`: Queries Qdrant using vector similarity via `client.search()` (direct, not langchain wrapper). Applies per-model threshold to filter irrelevant context.
  - `Generator`: Uses LangChain + Gemini/OpenAI to generate answers. Enforces a hard fallback if context is empty.
  - `FallbackAgent`: Dedicated module for the Katzilla web search agent. Instantiated once in `Generator.__init__` (not per-call).

- **Evaluation Domain (`eval`)**: Independent Python package containing datasets, metrics, and tests. Imports from the RAG domain to test components in isolation. Provider-agnostic (supports Gemini or OpenAI as judge).

- **Logging (`app/core/logging.py`)**: Structured JSON logging to stdout. All modules use `get_logger(__name__)`. Logs are parseable by cloud aggregators (Render, Datadog, CloudWatch).

### Data Flow (Chat)

1. User sends query to `/api/chat`.
2. Rate limiter checks (10/min default).
3. `Retriever` embeds the query via DirectGeminiEmbeddings and searches Qdrant directly.
4. Context is filtered by per-model similarity threshold.
5. `Generator` receives context and query. If context is empty:
   - If `KATZILLA_API_KEY` is set: delegates to `FallbackAgent` (LangChain tool calling).
   - Otherwise: returns hardcoded refusal (bypasses LLM entirely).
6. If context exists: prompts LLM with strict system instructions.
7. Response and sources returned to user.

### Data Flow (Ingestion)

1. Admin uploads file to `/api/ingest` with `X-API-Key` header (if `INGEST_API_KEY` is set).
2. Rate limiter checks (5/min default).
3. File saved to temp path, loaded by LangChain document loader (PDF/TXT/MD).
4. `RecursiveCharacterTextSplitter` chunks text (600 chars, 100 overlap).
5. Metadata (source_file, chunk_index) added to each chunk.
6. DirectGeminiEmbeddings embeds all chunks (batch of 5, with retry).
7. `client.upsert()` with `PointStruct` persists vectors + payload to Qdrant.
8. Temp file deleted.

### Async I/O

All sync LangChain/Qdrant/Gemini calls are wrapped with `starlette.concurrency.run_in_threadpool` to avoid blocking the FastAPI event loop. This allows concurrent request handling while keeping the RAG logic synchronous (simpler to reason about, accurate latency measurement).
