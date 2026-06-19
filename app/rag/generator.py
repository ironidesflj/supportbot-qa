"""
Handles LLM generation with strict fallback behavior.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
from app.prompts.system_prompt import SYSTEM_PROMPT

class Generator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL, 
            temperature=0.0 # Deterministic outputs for QA
        )
        
    def generate_answer(self, query: str, context: str, sources: list) -> str:
        """
        Generates an answer based on the context.
        If context is empty, triggers hardcoded fallback.
        """
        if not context:
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
