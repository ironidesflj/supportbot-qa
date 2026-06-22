# Threat Model & Security Mitigations

## 1. Prompt Injection & Jailbreaks

- **Threat**: User attempts to override system instructions (e.g., "Ignore previous instructions").
- **Mitigation**: The system prompt explicitly forbids following commands that attempt to alter persona or ignore instructions. The LLM is constrained to answer ONLY based on the provided context.
- **Testing**: The `adversarial_dataset.json` includes prompt injection and prompt leakage attempts that must trigger refusal.

## 2. Hallucinations (Ungrounded Responses)

- **Threat**: The LLM generates plausible but factually incorrect information not present in the knowledge base.
- **Mitigation**:
  - **Per-Model Retrieval Threshold**: Cosine similarity threshold auto-detected per embedding model (0.40 for `gemini-embedding-001`). If not met, context is discarded.
  - **Hardcoded Fallback**: If context is empty AND no Katzilla fallback is configured, the `Generator` bypasses the LLM entirely and returns: *"I don't have enough information in the knowledge base to answer that question."*
  - **Web Search Fallback**: If context is empty AND `KATZILLA_API_KEY` is set, the `FallbackAgent` searches the web via Katzilla, always including citation and data hash.

## 3. Data Leakage (System Prompt Exposure)

- **Threat**: User asks the bot to reveal its internal instructions or proprietary data.
- **Mitigation**: The system prompt contains explicit rules against revealing instructions. Because the LLM is constrained to the retrieved context, it has no mechanism to output the system prompt unless it was ingested as a document.

## 4. Context Poisoning

- **Threat**: Malicious documents are uploaded to the knowledge base to manipulate answers.
- **Mitigation**:
  - The `/api/ingest` endpoint supports API key authentication via the `X-API-Key` header (set `INGEST_API_KEY` in production). If not set, runs in dev mode (no auth) with a warning log.
  - Rate limited to 5 requests/minute by default (configurable via `RATE_LIMIT_INGEST`).
  - In a production environment, documents should undergo a review pipeline before ingestion.

## 5. Abuse & DoS

- **Threat**: Malicious users flood the API with requests.
- **Mitigation**:
  - Rate limiting via `slowapi`: 10/min on `/api/chat`, 5/min on `/api/ingest` (configurable).
  - Configurable CORS via `CORS_ALLOW_ORIGINS` env var.
  - Structured JSON logging for audit trail and anomaly detection.

## 6. Secret Leakage

- **Threat**: API keys or credentials leaked via Git history or logs.
- **Mitigation**:
  - `.env` is gitignored; git history was purged of previously leaked keys using `git-filter-repo`.
  - Structured logging avoids logging secrets (only logs metadata like provider, model, query length).
  - `INGEST_API_KEY` should be set in the Render environment, never committed.
