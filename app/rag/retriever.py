"""Handles vector search and context retrieval."""
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

class Retriever:
    """Handles context retrieval from the vector store."""
    
    def __init__(self):
        """Initializes the retriever with embeddings and Qdrant vector store."""
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            embeddings=self.embeddings
        )

    def retrieve_context(self, query: str) -> tuple[str, list]:
        """Retrieves relevant context and applies a similarity threshold.
        
        Returns a tuple of (formatted_context, list_of_source_documents).
        """
        # search_kwargs allows filtering and scoring
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=settings.RETRIEVAL_TOP_K
        )
        
        filtered_chunks = []
        sources = []
        
        for doc, score in results:
            # Qdrant returns distance, lower is better for Euclidean, but for Cosine, 
            # Qdrant client returns similarity score directly (higher is better).
            if score >= settings.SIMILARITY_THRESHOLD:
                filtered_chunks.append(doc.page_content)
                sources.append(doc.metadata.get("source_file", "Unknown"))
        
        if not filtered_chunks:
            return "", []
            
        context_str = "\n\n---\n\n".join(filtered_chunks)
        return context_str, list(set(sources))
