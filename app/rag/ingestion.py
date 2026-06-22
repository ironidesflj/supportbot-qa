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
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid

from app.rag.embeddings import DirectGeminiEmbeddings

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
            self.embeddings = DirectGeminiEmbeddings(
                model=settings.EMBEDDING_MODEL,
                api_key=settings.GEMINI_API_KEY,
                batch_size=5,
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
            # OpenAI's text-embedding-3-small uses 1536. 
            # Gemini's gemini-embedding-001 uses 3072.
            vector_size = 1536 if settings.LLM_PROVIDER == "openai" else 3072
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
        filename = os.path.basename(file_path)
        for idx, chunk in enumerate(chunks):
            chunk.metadata["source_file"] = filename
            chunk.metadata["chunk_index"] = idx

        self._ensure_collection_exists()

        # Embed all chunks via DirectGeminiEmbeddings (handles batching+retry).
        texts = [chunk.page_content for chunk in chunks]
        vectors = self.embeddings.embed_documents(texts)

        # Upsert points manually to ensure metadata is persisted in payload.
        # langchain-qdrant 0.1.3's add_documents does not reliably persist
        # metadata, so we use PointStruct directly.
        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "page_content": chunk.page_content,
                    "source_file": chunk.metadata.get("source_file", "Unknown"),
                    "chunk_index": chunk.metadata.get("chunk_index", 0),
                },
            ))

        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points,
        )
        return len(chunks)
