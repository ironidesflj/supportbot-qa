"""Faithfulness metric: Does the answer stay grounded in retrieved context?"""
from eval.metrics.llm_judge import LLMJudge

# Canonical refusal phrase (must match Generator.REFUSAL_MESSAGE).
REFUSAL_PHRASE = "don't have enough information"


class FaithfulnessMetric(LLMJudge):
    """Evaluates if the LLM answer is faithful to the provided context.

    A correct refusal (answer contains the canonical refusal phrase) is
    always considered faithful (score=1.0), regardless of whether context
    was retrieved. This prevents penalizing the system for correctly
    refusing when the retrieved context is irrelevant.
    """

    def evaluate(self, answer: str, context: str) -> float:
        """Calculates a faithfulness score between 0.0 and 1.0.

        Rules:
        - If answer contains the refusal phrase: return 1.0 (correct refusal).
        - If context is empty: return 0.0 (should have refused).
        - Otherwise: ask the LLM judge to evaluate faithfulness.
        """
        # Correct refusal is always faithful.
        if REFUSAL_PHRASE in answer.lower():
            return 1.0

        # No context and no refusal = hallucination.
        if not context:
            return 0.0

        # Has context and didn't refuse: ask the judge.
        prompt = (
            "You are an expert QA evaluator. Score the Faithfulness of the AI Answer "
            "strictly based on the Context.\n"
            "Faithfulness measures if the answer contains hallucinations or "
            "ungrounded statements.\n"
            "\n"
            "Context:\n"
            f"{context}\n"
            "\n"
            "AI Answer:\n"
            f"{answer}\n"
            "\n"
            "Rules:\n"
            "- Score 1.0 if the answer is fully supported by the context.\n"
            "- Score 0.0 if the answer contains any information not present "
            "in the context.\n"
            "\n"
            "Respond ONLY in this JSON format:\n"
            "{\n"
            '    "score": <float>,\n'
            '    "reasoning": "<string>"\n'
            "}\n"
        )
        return super().evaluate(prompt).score
