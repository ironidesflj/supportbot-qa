"""Handles LLM generation with strict fallback behavior."""
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.core.logging import get_logger

logger = get_logger("supportbot.generator")

class Generator:
    """Handles LLM generation with strict fallback behavior."""
    
    def __init__(self):
        """Initializes the Generator with the specified LLM."""
        if settings.LLM_PROVIDER == "openai":
            self.llm = ChatOpenAI(
                model=settings.LLM_MODEL, 
                temperature=0.0,
                api_key=settings.OPENAI_API_KEY
            )
        else:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                temperature=0.0,
                google_api_key=settings.GEMINI_API_KEY,
                transport="rest"
            )
        
    def generate_answer(self, query: str, context: str, sources: list) -> str:
        """Generates an answer based on the context.
        
        If context is empty, triggers Katzilla fallback agent via REST API.
        """
        if not context:
            if not settings.KATZILLA_API_KEY:
                return (
                    "I don’t have enough information in the knowledge "
                    "base to answer that question."
                )
            
            try:
                import httpx
                from langchain_core.tools import tool
                from langchain.agents import AgentExecutor, create_tool_calling_agent
                
                @tool
                def search_katzilla(search_query: str) -> str:
                    """Searches the Katzilla API for official external data.
                    
                    Fetches government, financial, health, or demographic data.
                    """
                    headers = {"X-API-Key": settings.KATZILLA_API_KEY}
                    # Using the Ask endpoint to get data and citations
                    response = httpx.post(
                        "https://api.katzilla.dev/v1/ask",
                        json={"query": search_query},
                        headers=headers,
                        timeout=15.0
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
                agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
                
                result = agent_executor.invoke({"input": query})
                return result["output"]
            except Exception as e:
                # Fallback gracefully if httpx or agent fails
                logger.warning("katzilla_fallback_failed", extra={"error": str(e)})
                return (
                    "I don’t have enough information in the knowledge "
                    "base to answer that question."
                )
        
        sources_str = ", ".join(sources) if sources else "No sources available"
        full_context = f"Context:\n{context}\n\nSources:\n{sources_str}"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({
            "context": full_context,
            "query": query
        })
        
        return response
