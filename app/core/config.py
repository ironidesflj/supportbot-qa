"""Application configuration and environment variables management."""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings class to manage environment variables."""
    
    # General
    APP_NAME: str = "SupportBot QA"
    ENVIRONMENT: str = "development"
    
    # LLM & Embeddings
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Vector DB (Qdrant)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "supportbot_kb"
    
    # RAG Parameters
    RETRIEVAL_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.75
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
