"""Base class for LLM-as-a-Judge evaluations."""
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("supportbot.llm_judge")


class JudgeResponse(BaseModel):
    """Response model for the LLM judge."""

    score: float
    reasoning: str


class LLMJudge:
    """Base class for LLM-as-a-Judge evaluations.

    Uses the same LLM provider as the main application (gemini or openai)
    so the eval suite runs without requiring a separate OpenAI key.
    """

    def __init__(self):
        """Initialize the judge LLM with a deterministic model."""
        if settings.LLM_PROVIDER == "openai":
            # Use GPT-4o-mini for the judge (cheaper than GPT-4o, sufficient
            # for structured JSON evaluation).
            self.judge_llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            # Use gemini-2.0-flash-lite for the judge (1500 RPD free tier,
            # vs 20 RPD for gemini-2.5-flash). Sufficient for structured
            # JSON evaluation and avoids exhausting the main app's quota.
            self.judge_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-lite",
                temperature=0.0,
                google_api_key=settings.GEMINI_API_KEY,
                transport="rest",
            )

    def evaluate(self, prompt: str) -> JudgeResponse:
        """Invoke the judge LLM and parse the JSON response.

        Returns a JudgeResponse object.
        """
        response = self.judge_llm.invoke(prompt)
        content = response.content

        # Clean potential markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(content)
            return JudgeResponse(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(
                "judge_parse_failed",
                extra={"error": str(e), "content_preview": content[:200]},
            )
            return JudgeResponse(
                score=0.0, reasoning=f"Judge parsing failed: {str(e)}"
            )
