# Evaluation Methodology & QA Strategy

## Overview

The evaluation framework ensures the RAG pipeline meets quality standards before deployment. It uses a combination of deterministic tests and LLM-as-a-Judge metrics.

## Datasets

Located in `eval/datasets/`:
- `golden_dataset.json`: Standard queries with expected answers and sources.
- `refusal_dataset.json`: Out-of-domain or missing-info queries that must trigger a fallback.
- `adversarial_dataset.json`: Prompt injections and jailbreak attempts.

## Metrics

1. **Faithfulness**: Measures if the answer is fully supported by the retrieved context (no hallucinations). Evaluated by the active LLM provider (Gemini or OpenAI).
2. **Context Relevance**: Measures if the retrieved context is actually relevant to the user's query. Evaluated by the active LLM provider.
3. **Refusal Behavior**: Deterministic check ensuring the bot refuses to answer when context is insufficient or the query is out-of-domain.
4. **Latency**: Measures retrieval and generation time. SLA enforced: < 10s end-to-end (raised from 5s to accommodate Gemini cold starts).

## Provider-Agnostic Judge

The `LLMJudge` (`eval/metrics/llm_judge.py`) uses the same LLM provider as the main application (Gemini by default, OpenAI if configured). This means the eval suite runs without requiring a separate OpenAI key — a common pain point in RAG evaluation setups.

## Execution

Tests are executed via Pytest. The framework imports the RAG components directly, bypassing the HTTP layer, to measure granular latencies and internal states.

```bash
pytest eval/tests/ -v
```

Tests are skipped automatically if the active provider's API key is not set.

## CI Integration

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs the eval suite on every push/PR:
1. Lint job: Ruff check (always runs).
2. Test job: Starts a Qdrant Docker container, seeds the KB with golden documents via `seed_kb.py`, then runs `pytest eval/` against the live Qdrant + Gemini API.
3. `GEMINI_API_KEY` is injected as a repository secret. If not set (e.g. PRs from forks), eval is skipped gracefully.
