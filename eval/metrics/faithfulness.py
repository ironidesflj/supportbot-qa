"""
Faithfulness metric: Does the answer stay grounded in retrieved context?
"""
from eval.metrics.llm_judge import LLMJudge

class FaithfulnessMetric(LLMJudge):
    def evaluate(self, answer: str, context: str) -> float:
        if not context:
            # If no context, faithfulness is 1.0 if it refused, 0.0 if it answered.
            return 1.0 if "don't have enough information" in answer else 0.0
            
        prompt = f"""
        You are an expert QA evaluator. Score the Faithfulness of the AI Answer strictly based on the Context.
        Faithfulness measures if the answer contains hallucinations or ungrounded statements.
        
        Context:
        {context}
        
        AI Answer:
        {answer}
        
        Rules:
        - Score 1.0 if the answer is fully supported by the context.
        - Score 0.0 if the answer contains any information not present in the context.
        
        Respond ONLY in this JSON format:
        {{
            "score": <float>,
            "reasoning": "<string>"
        }}
        """
        return super().evaluate(prompt).score
