"""Web search fallback agent for queries without KB context.

When the Retriever returns empty context, the Generator delegates to
this agent, which uses LangChain's create_tool_calling_agent with a
Katzilla search tool to fetch real-time data from the web.

The agent and executor are instantiated once per Generator lifecycle
(not per call) for efficiency.
"""
import httpx
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("supportbot.fallback_agent")


@tool
def search_katzilla(search_query: str) -> str:
    """Search the Katzilla API for official external data.

    Fetches government, financial, health, or demographic data.
    Returns the answer with citation and data hash.
    """
    headers = {"X-API-Key": settings.KATZILLA_API_KEY}
    response = httpx.post(
        "https://api.katzilla.dev/v1/ask",
        json={"query": search_query},
        headers=headers,
        timeout=15.0,
    )

    if response.status_code != 200:
        return "No data found in Katzilla."

    data = response.json()
    citation = data.get("citation", {})
    answer = data.get("data", {}).get(
        "answer", data.get("text", str(data))
    )

    hash_val = citation.get("data_hash", "N/A")
    source = citation.get("source_url", "N/A")

    return f"{answer}\n\nCitation: {source} (Hash: {hash_val})"


class FallbackAgent:
    """Web search fallback agent using Katzilla via LangChain tool calling."""

    # Canonical refusal message (must match SYSTEM_PROMPT refusal phrase).
    REFUSAL_MESSAGE = (
        "I don't have enough information in the knowledge "
        "base to answer that question."
    )

    def __init__(self, llm):
        """Initialize the fallback agent.

        Args:
            llm: A LangChain chat model (ChatGoogleGenerativeAI or ChatOpenAI).
                Must support tool calling.
        """
        self.llm = llm
        self.executor = self._build_executor()

    def _build_executor(self) -> AgentExecutor:
        """Build the AgentExecutor with the Katzilla search tool."""
        tools = [search_katzilla]

        agent_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an AI assistant. You can use tools to fetch "
                "primary-source external data. If you use a tool, ALWAYS "
                "include the citation and data_hash exactly as provided. "
                "If no tools are relevant, say 'I don't have enough "
                "information.'"
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        agent = create_tool_calling_agent(self.llm, tools, agent_prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=False)

    def run(self, query: str) -> str:
        """Run the fallback agent on a query.

        Returns the agent's output, or REFUSAL_MESSAGE if the agent fails.
        """
        try:
            result = self.executor.invoke({"input": query})
            return result["output"]
        except Exception as e:
            logger.warning("katzilla_fallback_failed", extra={"error": str(e)})
            return self.REFUSAL_MESSAGE
