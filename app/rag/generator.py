"""Handles LLM generation with strict fallback behavior."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
from app.prompts.system_prompt import SYSTEM_PROMPT

class Generator:
    """Handles LLM generation with strict fallback behavior."""
    
    def __init__(self):
        """Initializes the Generator with the specified LLM."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL, 
            temperature=0.0, # Deterministic outputs for QA
            api_key=settings.OPENAI_API_KEY
        )
        
    def generate_answer(self, query: str, context: str, sources: list) -> str:
        """Generates an answer based on the context.
        
        If context is empty, triggers Katzilla fallback agent.
        """
        if not context:
            if not settings.KATZILLA_API_KEY:
                return "I don’t have enough information in the knowledge base to answer that question."
            
            try:
                from katzilla.langchain import get_katzilla_tools
                from langchain.agents import AgentExecutor, create_openai_tools_agent
                
                tools = get_katzilla_tools(
                    api_key=settings.KATZILLA_API_KEY
                )
                
                agent_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an AI assistant. You can use tools to fetch primary-source external data. If you use a tool, ALWAYS include the citation and data_hash exactly as provided. If no tools are relevant, say 'I don't have enough information.'"),
                    ("human", "{input}"),
                    ("placeholder", "{agent_scratchpad}")
                ])
                
                agent = create_openai_tools_agent(self.llm, tools, agent_prompt)
                agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
                
                result = agent_executor.invoke({"input": query})
                return result["output"]
            except ImportError:
                return "I don’t have enough information in the knowledge base to answer that question."
        
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
