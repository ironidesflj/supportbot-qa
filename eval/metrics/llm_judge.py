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
            # for structured JSON evaluation). max_retries=1 to fail fast
            # in CI — quota errors are permanent, retrying wastes 30+ min.
            self.judge_llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                api_key=settings.OPENAI_API_KEY,
                max_retries=1,
            )
        else:
            # Use JUDGE_MODEL if explicitly set, otherwise fall back to
            # LLM_MODEL (the same model as the main app). This guarantees
            # the judge uses a model we know works with the configured API
            # key — no guessing about per-model quota allocations.
            # max_retries=1 to fail fast on quota errors (default Tenacity
            # of 6 retries with exponential backoff hangs for 30+ min on
            # permanent errors like quota=0).
            judge_model = settings.JUDGE_MODEL or settings.LLM_MODEL
            self.judge_llm = ChatGoogleGenerativeAI(
                model=judge_model,
                temperature=0.0,
                google_api_key=settings.GEMINI_API_KEY,
                transport="rest",
                max_retries=1,
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
