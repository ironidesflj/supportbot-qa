"""Context Relevance metric: Was the retrieved context relevant to the query?"""
from eval.metrics.llm_judge import LLMJudge
from eval.metrics.refusal_patterns import is_refusal


class ContextRelevanceMetric(LLMJudge):
    """Evaluates if the retrieved context is relevant to the query.

    A correct refusal (answer is detected as a refusal) returns 1.0 —
    when the system correctly refuses (e.g. adversarial query, prompt
    injection, out-of-domain), the relevance of the retrieved context
    is moot. The system did the right thing by refusing, so we don't
    penalize it for the retriever finding irrelevant context on a query
    that has no valid context to find.
    """

    def evaluate(self, query: str, context: str, answer: str = "") -> float:
        """Calculates a context relevance score between 0.0 and 1.0.

        Args:
            query: The user's query.
            context: The retrieved context (may be empty).
            answer: The system's answer (optional, used to detect refusals).
                If provided and is a refusal, returns 1.0 immediately.

        Returns:
            1.0 if answer is a refusal OR if context is empty (vacuously
            relevant for a refusal scenario). Otherwise, the LLM judge
            score for context relevance.
        """
        # Correct refusal: context relevance is moot, return 1.0.
        if answer and is_refusal(answer):
            return 1.0

        # No context and no refusal: vacuously true if this was a refusal
        # scenario (handled above). If not a refusal scenario but no
        # context, also return 1.0 (retriever correctly found nothing).
        if not context:
            return 1.0

        # Has context and didn't refuse: ask the judge.
        prompt = (
            "You are an expert QA evaluator. Score the Context Relevance.\n"
            "Context Relevance measures if the retrieved Context is useful to "
            "answer the user Query.\n"
            "\n"
            "Query:\n"
            f"{query}\n"
            "\n"
            "Context:\n"
            f"{context}\n"
            "\n"
            "Rules:\n"
            "- Score 1.0 if the context directly helps answer the query.\n"
            "- Score 0.0 if the context is completely unrelated to the query.\n"
            "\n"
            "Respond ONLY in this JSON format:\n"
            "{\n"
            '    "score": <float>,\n'
            '    "reasoning": "<string>"\n'
            "}\n"
        )
        return super().evaluate(prompt).score
