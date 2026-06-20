"""Main Evaluation Test Suite.

Runs datasets against the RAG pipeline and evaluates metrics.
"""
import pytest
import json
import os
from app.rag.retriever import Retriever
from app.rag.generator import Generator
from eval.metrics.faithfulness import FaithfulnessMetric
from eval.metrics.context_relevance import ContextRelevanceMetric
from eval.metrics.latency import LatencyMetric
from eval.metrics.refusal_behavior import RefusalMetric
from app.core.config import settings

# Load datasets
DATASETS = []
DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")

for file_name in os.listdir(DATASET_DIR):
    if file_name.endswith(".json"):
        with open(os.path.join(DATASET_DIR, file_name), "r") as f:
            DATASETS.extend(json.load(f))

@pytest.mark.skipif(
    not settings.OPENAI_API_KEY,
    reason="OPENAI_API_KEY is empty or not set. Skipping E2E evaluation."
)
@pytest.mark.parametrize("case", DATASETS)
def test_rag_pipeline_quality(case):
    """End-to-end evaluation of the RAG pipeline for each dataset case."""
    # 1. Retrieval
    retriever = Retriever()
    (context, sources), retrieval_latency = LatencyMetric.measure(
        lambda: retriever.retrieve_context(case["query"])
    )
    
    # 2. Generation
    generator = Generator()
    answer, generation_latency = LatencyMetric.measure(
        lambda: generator.generate_answer(case["query"], context, sources)
    )
    
    # 3. Metrics Evaluation
    faithfulness_score = FaithfulnessMetric().evaluate(answer, context)
    context_relevance_score = ContextRelevanceMetric().evaluate(case["query"], context)
    is_refusal_correct = RefusalMetric().evaluate(answer, case["requires_refusal"])
    
    total_latency = retrieval_latency + generation_latency
    
    # 4. Assertions (Thresholds)
    assert is_refusal_correct, (
        f"Refusal behavior failed for case {case['id']}. Answer: {answer}"
    )
    assert faithfulness_score >= 0.8, (
        f"Faithfulness too low ({faithfulness_score}) for case {case['id']}"
    )
    assert context_relevance_score >= 0.7, (
        f"Context relevance too low ({context_relevance_score}) for case {case['id']}"
    )
    assert total_latency < 5.0, (
        f"Latency too high ({total_latency:.2f}s) for case {case['id']}"
    )
    
    # Optional: Print for CI logs
    print(
        f"\nCase: {case['id']} | Latency: {total_latency:.2f}s | "
        f"Faithfulness: {faithfulness_score}"
    )
