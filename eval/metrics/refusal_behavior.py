"""Refusal Behavior metric: Checks if the system refused correctly when needed."""
from eval.metrics.refusal_patterns import is_refusal


class RefusalMetric:
    """Evaluates if the system correctly refused to answer when appropriate.

    Uses the shared is_refusal() function from refusal_patterns.py to
    detect refusals. This ensures consistency with FaithfulnessMetric.
    """

    def evaluate(self, answer: str, requires_refusal: bool) -> bool:
        """Returns True if refusal behavior is correct, False otherwise.

        Args:
            answer: The system's answer.
            requires_refusal: Whether this case should have been refused.

        Returns:
            True if the refusal behavior is correct (refused when required,
            or didn't refuse when not required).
        """
        contains_refusal = is_refusal(answer)

        if requires_refusal:
            return contains_refusal
        else:
            return not contains_refusal
