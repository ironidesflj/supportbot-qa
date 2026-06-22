"""Base class for LLM-as-a-Judge evaluations."""
import json
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, ValidationError
from app.core.config import settings


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
        """Initializes the judge LLM with a deterministic model."""
        if settings.LLM_PROVIDER == "openai":
            self.judge_llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.0,
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            self.judge_llm = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                temperature=0.0,
                google_api_key=settings.GEMINI_API_KEY,
                transport="rest",
            )

    def evaluate(self, prompt: str) -> JudgeResponse:
        """Invokes the judge LLM and parses the JSON response.

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
            return JudgeResponse(
                score=0.0, reasoning=f"Judge parsing failed: {str(e)}"
            )
