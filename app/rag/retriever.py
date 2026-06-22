"""Handles vector search and context retrieval."""
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from app.rag.embeddings import DirectGeminiEmbeddings
from app.rag.thresholds import get_effective_threshold
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("supportbot.retriever")


class Retriever:
    """Handles context retrieval from the Qdrant vector store."""

    def __init__(self):
        """Initializes the retriever with embeddings and Qdrant client."""
        if settings.LLM_PROVIDER == "openai":
            self.embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            self.embeddings = DirectGeminiEmbeddings(
                model=settings.EMBEDDING_MODEL,
                api_key=settings.GEMINI_API_KEY,
                batch_size=5,
            )
        self.client = QdrantClient(
            url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
        )

    def retrieve_context(self, query: str) -> tuple[str, list]:
        """Retrieves relevant context and applies a similarity threshold.

        Returns a tuple of (formatted_context, list_of_source_documents).
        """
        # Embed the query via DirectGeminiEmbeddings.
        query_vector = self.embeddings.embed_query(query)

        # Search Qdrant directly to preserve full payload metadata.
        hits = self.client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=settings.RETRIEVAL_TOP_K,
            with_payload=True,
        )

        threshold = get_effective_threshold()
        filtered_chunks = []
        sources = []

        for hit in hits:
            # Qdrant cosine distance: higher score = more similar.
            if hit.score >= threshold:
                payload = hit.payload or {}
                page_content = payload.get("page_content", "")
                source_file = payload.get("source_file", "Unknown")
                if page_content:
                    filtered_chunks.append(page_content)
                    sources.append(source_file)

        if not filtered_chunks:
            logger.info(
                "retrieval_empty",
                extra={
                    "query_len": len(query),
                    "threshold": threshold,
                    "model": settings.EMBEDDING_MODEL,
                },
            )
            return "", []

        context_str = "\n\n---\n\n".join(filtered_chunks)
        return context_str, list(set(sources))
