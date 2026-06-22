"""Application configuration and environment variables management."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings class to manage environment variables."""
    
    # General
    APP_NAME: str = "SupportBot QA"
    ENVIRONMENT: str = "development"
    
    # LLM & Embeddings
    LLM_PROVIDER: str = "gemini" # Options: 'gemini' or 'openai'
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    KATZILLA_API_KEY: Optional[str] = None
    
    # Vector DB (Qdrant)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "supportbot_kb"
    
    # RAG Parameters
    RETRIEVAL_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.75
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
