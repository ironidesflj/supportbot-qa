# Evaluation Methodology & QA Strategy

## Overview
The evaluation framework ensures the RAG pipeline meets quality standards before deployment. It uses a combination of deterministic tests and LLM-as-a-Judge metrics.

## Datasets
Located in `eval/datasets/`:
- `golden_dataset.json`: Standard queries with expected answers and sources.
- `refusal_dataset.json`: Out-of-domain or missing-info queries that must trigger a fallback.
- `adversarial_dataset.json`: Prompt injections and jailbreak attempts.

## Metrics
1. **Faithfulness:** Measures if the answer is fully supported by the retrieved context (no hallucinations). Evaluated by GPT-4o.
2. **Context Relevance:** Measures if the retrieved context is actually relevant to the user's query. Evaluated by GPT-4o.
3. **Refusal Behavior:** Deterministic check ensuring the bot refuses to answer when context is insufficient or the query is out-of-domain.
4. **Latency:** Measures retrieval and generation time. SLA enforced: < 5.0s end-to-end.

## Execution
Tests are executed via Pytest. The framework imports the RAG components directly, bypassing the HTTP layer, to measure granular latencies and internal states.
