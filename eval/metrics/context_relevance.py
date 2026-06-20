"""
Context Relevance metric: Was the retrieved context actually relevant to the query?
"""
from eval.metrics.llm_judge import LLMJudge

class ContextRelevanceMetric(LLMJudge):
    """Evaluates if the retrieved context is relevant to the query."""
    
    def evaluate(self, query: str, context: str) -> float:
        """Calculates a context relevance score between 0.0 and 1.0."""
        if not context:
            # Vacuously true if no context was retrieved for a refusal scenario
            return 1.0
            
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
