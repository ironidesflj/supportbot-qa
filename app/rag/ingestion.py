"""Handles document ingestion, chunking, and vectorization into Qdrant."""
import os
from typing import List
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings

class IngestionPipeline:
    """Pipeline for loading, chunking, and embedding documents into Qdrant."""
    
    def __init__(self):
        """Initializes pipeline with embeddings and Qdrant connection."""
        if settings.LLM_PROVIDER == "openai":
            self.embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
        self.client = QdrantClient(
            url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def _load_document(self, file_path: str) -> List:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path)
        elif ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        return loader.load()

    def _ensure_collection_exists(self):
        # Check if collection exists, create if not
        try:
            self.client.get_collection(settings.QDRANT_COLLECTION_NAME)
        except Exception:
            # OpenAI's text-embedding-3-small uses 1536. Gemini's text-embedding-004 uses 768.
            vector_size = 1536 if settings.LLM_PROVIDER == "openai" else 768
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )

    def ingest(self, file_path: str) -> int:
        """Ingests a single document into the vector store.
        
        Returns the number of chunks added. Returns 0 if document is empty.
        """
        documents = self._load_document(file_path)
        chunks = self.text_splitter.split_documents(documents)
        
        if not chunks:
            return 0
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata["source_file"] = os.path.basename(file_path)

        self._ensure_collection_exists()
        
        QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name=settings.QDRANT_COLLECTION_NAME
        )
        return len(chunks)
