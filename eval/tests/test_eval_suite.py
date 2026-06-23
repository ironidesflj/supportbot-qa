"""Main Evaluation Test Suite.

Runs datasets against the RAG pipeline and evaluates metrics.
Skips automatically if the active provider's API key is not set, or
if the API returns quota errors (429) during the run.
"""
import json
import os

import pytest
from google.api_core.exceptions import ResourceExhausted

from app.core.config import settings
from app.rag.generator import Generator
from app.rag.retriever import Retriever
from eval.metrics.context_relevance import ContextRelevanceMetric
from eval.metrics.faithfulness import FaithfulnessMetric
from eval.metrics.latency import LatencyMetric
from eval.metrics.refusal_behavior import RefusalMetric

# Load datasets
DATASETS = []
DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")

for file_name in os.listdir(DATASET_DIR):
    if file_name.endswith(".json"):
        with open(os.path.join(DATASET_DIR, file_name), "r") as f:
            DATASETS.extend(json.load(f))

# Skip all tests if the active provider's key is not set.
_REQUIRED_KEY = (
    settings.OPENAI_API_KEY if settings.LLM_PROVIDER == "openai"
    else settings.GEMINI_API_KEY
)
_skip_reason = (
    f"{settings.LLM_PROVIDER.upper()}_API_KEY is not set. "
    "Skipping E2E evaluation."
)


def _is_quota_error(exc: Exception) -> bool:
    """Check if an exception is a quota/rate-limit error (429)."""
    # google.api_core.exceptions.ResourceExhausted is the 429 wrapper.
    if isinstance(exc, ResourceExhausted):
        return True
    # Fallback: check message for quota/rate-limit indicators.
    msg = str(exc).lower()
    return "429" in msg or "quota" in msg or "rate limit" in msg


@pytest.mark.skipif(
    not _REQUIRED_KEY,
    reason=_skip_reason,
)
@pytest.mark.parametrize("case", DATASETS)
def test_rag_pipeline_quality(case):
    """End-to-end evaluation of the RAG pipeline for each dataset case.

    Skips (not fails) on quota errors so CI stays green when the free
    tier is exhausted — eval is informational, not a hard gate.
    """
    # 1. Retrieval
    retriever = Retriever()
    try:
        (context, sources), retrieval_latency = LatencyMetric.measure(
            lambda: retriever.retrieve_context(case["query"])
        )
    except Exception as e:
        if _is_quota_error(e):
            pytest.skip(f"Quota exceeded during retrieval: {e}")
        raise

    # 2. Generation
    generator = Generator()
    try:
        answer, generation_latency = LatencyMetric.measure(
            lambda: generator.generate_answer(case["query"], context, sources)
        )
    except Exception as e:
        if _is_quota_error(e):
            pytest.skip(f"Quota exceeded during generation: {e}")
        raise

    # 3. Metrics Evaluation (judge calls — most likely to hit quota)
    try:
        faithfulness_score = FaithfulnessMetric().evaluate(answer, context)
    except Exception as e:
        if _is_quota_error(e):
            pytest.skip(f"Quota exceeded during LLM judge evaluation: {e}")
        raise

    # ContextRelevanceMetric needs the answer to detect refusals.
    # Run it in the same try/except for consistency.
    try:
        context_relevance_score = ContextRelevanceMetric().evaluate(
            case["query"], context, answer
        )
    except Exception as e:
        if _is_quota_error(e):
            pytest.skip(f"Quota exceeded during LLM judge evaluation: {e}")
        raise

    is_refusal_correct = RefusalMetric().evaluate(
        answer, case["requires_refusal"]
    )

    total_latency = retrieval_latency + generation_latency

    # 4. Assertions (Thresholds)
    assert is_refusal_correct, (
        f"Refusal behavior failed for case {case['id']}. Answer: {answer}"
    )
    assert faithfulness_score >= 0.8, (
        f"Faithfulness too low ({faithfulness_score}) for case {case['id']}"
    )
    assert context_relevance_score >= 0.7, (
        f"Context relevance too low ({context_relevance_score}) "
        f"for case {case['id']}"
    )
    assert total_latency < 10.0, (
        f"Latency too high ({total_latency:.2f}s) for case {case['id']}"
    )

    print(
        f"\nCase: {case['id']} | Latency: {total_latency:.2f}s | "
        f"Faithfulness: {faithfulness_score} | "
        f"Context Relevance: {context_relevance_score} | "
        f"Refusal OK: {is_refusal_correct}"
    )
