"""Handles LLM generation with strict fallback behavior."""
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
from app.core.logging import get_logger
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.rag.fallback_agent import FallbackAgent

logger = get_logger("supportbot.generator")


class Generator:
    """Handles LLM generation with strict fallback behavior."""

    # Canonical refusal message (matches SYSTEM_PROMPT).
    REFUSAL_MESSAGE = (
        "I don't have enough information in the knowledge "
        "base to answer that question."
    )

    def __init__(self):
        """Initialize the Generator with the specified LLM and fallback agent."""
        if settings.LLM_PROVIDER == "openai":
            self.llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=0.0,
                api_key=settings.OPENAI_API_KEY,
                max_retries=2,
            )
        else:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                temperature=0.0,
                google_api_key=settings.GEMINI_API_KEY,
                transport="rest",
                max_retries=2,
            )

        # Fallback agent is only built if Katzilla key is configured.
        # Otherwise, empty context always returns REFUSAL_MESSAGE.
        self.fallback_agent = None
        if settings.KATZILLA_API_KEY:
            try:
                self.fallback_agent = FallbackAgent(self.llm)
                logger.info("fallback_agent_initialized")
            except Exception as e:
                logger.warning(
                    "fallback_agent_init_failed",
                    extra={"error": str(e)},
                )

    def generate_answer(self, query: str, context: str, sources: list) -> str:
        """Generate an answer based on the context.

        If context is empty, triggers the Katzilla fallback agent (if
        configured) or returns the canonical refusal message.
        """
        if not context:
            if self.fallback_agent:
                return self.fallback_agent.run(query)
            return self.REFUSAL_MESSAGE

        sources_str = ", ".join(sources) if sources else "No sources available"
        full_context = f"Context:\n{context}\n\nSources:\n{sources_str}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{query}"),
        ])

        chain = prompt | self.llm | StrOutputParser()

        response = chain.invoke({
            "context": full_context,
            "query": query,
        })

        return response
