"""
Context Relevance metric: Was the retrieved context actually relevant to the query?
"""
from eval.metrics.llm_judge import LLMJudge

class ContextRelevanceMetric(LLMJudge):
    def evaluate(self, query: str, context: str) -> float:
        if not context:
            return 1.0 # Vacuously true if no context was retrieved for a refusal scenario
            
        prompt = f"""
        You are an expert QA evaluator. Score the Context Relevance.
        Context Relevance measures if the retrieved Context is useful to answer the user Query.
        
        Query:
        {query}
        
        Context:
        {context}
        
        Rules:
        - Score 1.0 if the context directly helps answer the query.
        - Score 0.0 if the context is completely unrelated to the query.
        
        Respond ONLY in this JSON format:
        {{
            "score": <float>,
            "reasoning": "<string>"
        }}
        """
        return super().evaluate(prompt).score
