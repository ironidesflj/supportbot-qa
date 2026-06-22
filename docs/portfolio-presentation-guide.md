# Portfolio Presentation Guide

This document guides how to present the "SupportBot QA" project in interviews and resume reviews.

## Elevator Pitch

"I built an enterprise-grade RAG customer support chatbot with a strong emphasis on AI Quality Assurance. Instead of just building a LangChain wrapper, I engineered a custom evaluation framework using LLM-as-a-Judge to test for faithfulness, context relevance, and prompt injection resistance, ensuring the bot meets strict latency and hallucination thresholds. When the LangChain Gemini wrapper proved unreliable with the new embedding model family, I bypassed it with a direct SDK integration — a decision that demonstrates pragmatic engineering over framework dogma."

## Key Talking Points for Interviews

### 1. Architecture & Engineering

- Discuss the **Modular Monolith** design. Why separating the `eval` module from the `app` module is crucial for testing internal components without HTTP overhead.
- Explain the **lifespan singleton pattern**: why instantiating Retriever/Generator/IngestionPipeline once on startup (not per-request) matters for performance.
- Discuss the **async I/O strategy**: `run_in_threadpool` to avoid blocking the event loop while keeping RAG logic synchronous for accurate latency measurement.
- Explain the ingestion pipeline (PDF/MD parsing, chunking with 600 chars, Qdrant upsert with explicit payload).

### 2. AI Quality Assurance (The Differentiator)

- Explain how the `LLMJudge` works. How did you handle malformed JSON from the LLM? (Markdown code block stripping + try/except with score=0.0 fallback.)
- Discuss the datasets (Golden, Adversarial, Refusal). Why is testing refusal behavior as important as testing correct answers?
- Explain the metrics: Faithfulness, Context Relevance, Latency (SLA < 10s), Refusal.
- Highlight that the judge is **provider-agnostic** — uses the same Gemini/OpenAI key as the app, no separate OpenAI key required for eval.

### 3. Pragmatic Engineering Decisions

- **DirectGeminiEmbeddings**: When the LangChain wrapper returned 504 (masking 404), I bypassed it with a direct SDK call. Discuss the tradeoff: more code to maintain, but full control and honest error messages.
- **Per-model thresholds**: Different embedding models have different score distributions. A lookup table (`thresholds.py`) is more robust than a hardcoded value.
- **Manual Qdrant payload**: When `langchain-qdrant` silently dropped metadata, I switched to `client.upsert()` with explicit `PointStruct`. More verbose, but 100% reliable.
- **FallbackAgent extraction**: Moved the Katzilla agent from inline (per-call) to a dedicated module (per-instance). Cleaner separation, easier to test.

### 4. Security & Reliability

- Talk about the **Threat Model**. How does the system resist prompt injection? (System prompt constraints + deterministic fallback).
- Explain the **per-model similarity threshold** (0.40 for gemini-embedding-001). How did you balance false positives vs. false negatives?
- Discuss **API key auth** on `/api/ingest` and **rate limiting** (slowapi) as production-readiness signals.
- Mention the **secret leak remediation**: git history purge with `git-filter-repo`, key rotation, comprehensive `.gitignore`.

### 5. DevOps & CI/CD

- Highlight the GitHub Actions pipeline: lint job (Ruff) + test job (Qdrant container + seed + pytest eval).
- Discuss Docker Compose orchestration for local development (Frontend, Backend, Qdrant).
- Mention the Render blueprint + Vercel deployment strategy.

### 6. Accessibility

- Mention the ARIA-compliant frontend (tabs, live regions, keyboard navigation, drag-and-drop). This shows maturity beyond just "it works" — it works for everyone.

## How to Run It for Interviewers

1. Show the `docker-compose up` command spinning up the whole stack.
2. Use the Frontend UI to upload a PDF (Ingestion) — demonstrate drag-and-drop.
3. Ask a question in the chat, then ask an out-of-domain question to demonstrate the hardcoded fallback.
4. Open a terminal and run `pytest eval/tests/ -v` to show the LLM-as-a-Judge evaluating the pipeline in real-time.
5. Show the structured JSON logs (`tail -f backend.log`) to demonstrate observability.

## Resume Bullet Points

- "Engineered a production-grade RAG customer support chatbot with FastAPI, React, Qdrant, and Google Gemini, featuring lifespan singletons, async I/O, structured JSON logging, rate limiting, and API key authentication."
- "Built a custom LLM-as-a-Judge evaluation framework (faithfulness, context relevance, refusal behavior, latency) with golden, adversarial, and refusal datasets, integrated into GitHub Actions CI with live Qdrant + Gemini."
- "Bypassed unreliable LangChain Gemini wrapper with a direct SDK integration (DirectGeminiEmbeddings) for reliable embeddings with per-model similarity thresholds and exponential backoff retry."
- "Implemented ARIA-compliant React frontend with drag-and-drop file upload, empty states, and structured error handling."
- "Remediated secret leak in Git history via git-filter-repo, rotated all credentials, and established comprehensive .gitignore and security practices."
