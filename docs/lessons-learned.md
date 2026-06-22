# Tradeoff Analysis & Lessons Learned

## 1. Custom LLM-as-a-Judge vs. Off-the-shelf Frameworks

**Tradeoff**: Building custom evaluation metrics from scratch required writing robust JSON parsers and handling LLM flakiness (e.g., models wrapping JSON in markdown). We could have used Ragas or DeepEval.

**Lesson**: For a portfolio project targeting Senior/Staff AI Engineer roles, custom metrics prove a deep understanding of how LLMs evaluate text. The effort to handle JSON parsing exceptions and strict prompt engineering for the judge was worth the demonstrable skill.

## 2. Hardcoded Fallback vs. LLM-driven Refusal

**Tradeoff**: We implemented a hardcoded fallback string when the Qdrant similarity threshold is not met, bypassing the LLM entirely.

**Lesson**: Relying on the LLM to decide when to refuse based on empty context often leads to occasional hallucinations ("creativity"). A deterministic, code-level hard stop guarantees 100% refusal behavior when context is missing, drastically improving the `RefusalMetric` scores and system safety.

## 3. Direct SDK vs. LangChain Wrapper for Gemini Embeddings

**Tradeoff**: The `langchain-google-genai` wrapper (v1.0.4) was incompatible with the new `gemini-embedding-*` model family. It called `batch_embed_contents` internally and returned 504 errors (masking 404 "model not found" errors). We could have upgraded the lib (requires Python 3.10+) or switched to OpenAI.

**Lesson**: Building a custom `DirectGeminiEmbeddings` class that calls `google.generativeai.embed_content()` directly gave us full control over the embedding call, explicit error messages, and production-grade retry with exponential backoff. This also made the codebase more resilient to future LangChain breaking changes. Sometimes bypassing the abstraction layer is the right call — abstractions should reduce complexity, not hide errors.

## 4. Per-Model Thresholds vs. Hardcoded Value

**Tradeoff**: We initially hardcoded `SIMILARITY_THRESHOLD=0.75` (tuned for `text-embedding-004`). When we migrated to `gemini-embedding-001`, the score distribution changed (good matches score 0.4-0.7 instead of 0.7-0.9), and the hardcoded threshold cut all valid results.

**Lesson**: Different embedding models have fundamentally different score distributions. A lookup table with per-model defaults (`app/rag/thresholds.py`) is more robust than a single hardcoded value. The env var override remains for advanced tuning.

## 5. Sync vs Async in RAG Components

**Tradeoff**: While FastAPI is async, the LangChain Qdrant and Gemini clients have varying levels of native async support depending on the version.

**Lesson**: To ensure accurate latency measurements without overcomplicating the thread pool execution, we kept the core RAG logic synchronous but wrapped it in `run_in_threadpool` at the FastAPI handler level. This gives us the best of both worlds: async request handling (no event loop blocking) and sync RAG logic (simpler to reason about, accurate latency measurement). In a high-throughput production system, migrating entirely to `AsyncOpenAI` and async Qdrant clients would be the next optimization step.

## 6. Lifespan Singletons vs. Per-Request Instantiation

**Tradeoff**: The original code instantiated `Retriever()`, `Generator()`, and `IngestionPipeline()` on every request, creating new Qdrant and Gemini clients each time.

**Lesson**: FastAPI's lifespan context manager is the right place for expensive singletons. Moving instantiation to startup eliminated redundant client creation, reduced latency, and made connection pooling more effective. This is a common performance pitfall in FastAPI apps.

## 7. Manual Payload Persistence vs. LangChain-Qdrant Wrapper

**Tradeoff**: The `langchain-qdrant` (v0.1.3) `QdrantVectorStore.add_documents()` did not reliably persist `Document.metadata` into the Qdrant payload, causing the Retriever to return "Unknown" as the source for all chunks.

**Lesson**: When an abstraction layer silently drops data, bypass it. We switched to `client.upsert()` with explicit `PointStruct` (setting payload with `page_content`, `source_file`, `chunk_index`) and `client.search()` for retrieval. More verbose, but 100% reliable. Always verify that abstractions preserve the data you care about.
