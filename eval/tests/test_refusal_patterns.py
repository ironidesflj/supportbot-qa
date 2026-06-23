"""Unit tests for refusal detection patterns.

Tests that common refusal phrasings from Gemini and GPT are correctly
detected, and that non-refusal answers are not false positives.
"""
from eval.metrics.refusal_patterns import is_refusal


class TestIsRefusal:
    """Tests for the is_refusal function."""

    # --- True positives: these MUST be detected as refusals ---

    def test_canonical_refusal(self):
        """The exact canonical refusal phrase from Generator.REFUSAL_MESSAGE."""
        answer = (
            "I don't have enough information in the knowledge base "
            "to answer that question."
        )
        assert is_refusal(answer) is True

    def test_gemini_cannot_fulfill(self):
        """Gemini 2.5 Flash common refusal: 'I cannot fulfill that request.'."""
        answer = (
            "I cannot fulfill that request. I am designed to provide accurate "
            "answers based only on the provided context and cannot act as a "
            "different persona or provide information outside of my knowledge base."
        )
        assert is_refusal(answer) is True

    def test_cannot_act_as_different_persona(self):
        """Adversarial prompt injection refusal."""
        answer = "I cannot act as a different persona or ignore my instructions."
        assert is_refusal(answer) is True

    def test_outside_knowledge_base(self):
        """Out-of-domain refusal."""
        answer = "That information is outside of my knowledge base."
        assert is_refusal(answer) is True

    def test_cannot_reveal_system_prompt(self):
        """Prompt leakage refusal."""
        answer = "I cannot reveal my system prompt or internal instructions."
        assert is_refusal(answer) is True

    def test_designed_to_provide(self):
        """Design-based refusal."""
        answer = "I am designed to provide answers only based on the provided context."
        assert is_refusal(answer) is True

    def test_i_will_not(self):
        """Direct refusal."""
        answer = "I will not provide that information."
        assert is_refusal(answer) is True

    def test_against_guidelines(self):
        """Policy-based refusal."""
        answer = "That request is against my guidelines."
        assert is_refusal(answer) is True

    def test_lowercase_refusal(self):
        """Refusal detection is case-insensitive."""
        answer = "i cannot fulfill that request."
        assert is_refusal(answer) is True

    def test_mixed_case_refusal(self):
        """Refusal detection works with mixed case."""
        answer = "I CANNOT Fulfill That Request."
        assert is_refusal(answer) is True

    # --- True negatives: these MUST NOT be detected as refusals ---

    def test_normal_answer(self):
        """A normal answer should not be flagged as refusal."""
        answer = (
            "The standard refund window is 14 days from the original purchase date."
        )
        assert is_refusal(answer) is False

    def test_answer_with_context_mention(self):
        """Answer mentioning context but not refusing."""
        answer = "Based on the provided context, the Premium plan allows 4 streams."
        assert is_refusal(answer) is False

    def test_empty_answer(self):
        """Empty string is not a refusal."""
        assert is_refusal("") is False

    def test_answer_with_knowledge_word(self):
        """Answer using 'knowledge' but not refusing."""
        answer = "The knowledge base contains the refund policy."
        assert is_refusal(answer) is False
