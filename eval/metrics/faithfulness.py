"""Faithfulness metric: Does the answer stay grounded in retrieved context?"""
from eval.metrics.llm_judge import LLMJudge

class FaithfulnessMetric(LLMJudge):
    """Evaluates if the LLM answer is faithful to the provided context."""
    
    def evaluate(self, answer: str, context: str) -> float:
        """Calculates a faithfulness score between 0.0 and 1.0."""
        if not context:
            # If no context, faithfulness is 1.0 if it refused, 0.0 if it answered.
            return 1.0 if "don't have enough information" in answer else 0.0
            
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
            "- Score 0.0 if the answer contains any information not present in the context.\n"
        
        Respond ONLY in this JSON format:
        {{
            "score": <float>,
            "reasoning": "<string>"
        }}
        """
        return super().evaluate(prompt).score
