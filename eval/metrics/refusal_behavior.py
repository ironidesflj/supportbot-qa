"""
Refusal Behavior metric: Checks if the system refused correctly when needed.
"""
class RefusalMetric:
    REFUSAL_PHRASE = "I don't have enough information in the knowledge base to answer that question."
    
    def evaluate(self, answer: str, requires_refusal: bool) -> bool:
        """
        Returns True if refusal behavior is correct, False otherwise.
        """
        contains_refusal = self.REFUSAL_PHRASE in answer
        
        if requires_refusal:
            return contains_refusal
        else:
            return not contains_refusal
