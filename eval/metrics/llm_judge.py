"""Base class for LLM-as-a-Judge evaluations."""
import json
from pydantic import BaseModel, ValidationError
from langchain_openai import ChatOpenAI

class JudgeResponse(BaseModel):
    """Response model for the LLM judge."""
    score: float
    reasoning: str

class LLMJudge:
    """Base class for LLM-as-a-Judge evaluations."""
    
    def __init__(self):
        """Initializes the LLM judge with a deterministic model."""
        self.judge_llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        
    def evaluate(self, prompt: str) -> JudgeResponse:
        """Invokes the judge LLM and parses the JSON response.
        
        Returns a JudgeResponse object.
        """
        response = self.judge_llm.invoke(prompt)
        content = response.content
        
        # Clean potential markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
            
        try:
            data = json.loads(content)
            return JudgeResponse(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            return JudgeResponse(score=0.0, reasoning=f"Judge parsing failed: {str(e)}")
