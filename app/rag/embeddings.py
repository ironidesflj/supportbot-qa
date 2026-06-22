"""Direct Google Gemini embeddings, bypassing langchain-google-genai wrapper.

The langchain-google-genai wrapper (v1.0.4) is incompatible with the new
gemini-embedding-* family of models (returns 504 masking a 404). This module
provides a custom LangChain Embeddings implementation that calls
google.generativeai.embed_content() directly, giving us:
- Full control over the embedding call (no hidden batch endpoint)
- Explicit error messages (no google-api-core retry masking)
- Production-grade retry with exponential backoff
- Compatibility with all current Gemini embedding models

Used by both IngestionPipeline and Retriever.
"""
import time
from typing import List

import google.generativeai as genai
from langchain_core.embeddings import Embeddings


class DirectGeminiEmbeddings(Embeddings):
    """LangChain Embeddings interface backed by google.generativeai directly.

    Call genai.embed_content() per batch (default 5 texts) with retry.
    Suitable for both ingestion (embed_documents) and query (embed_query).
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        batch_size: int = 5,
        max_retries: int = 3,
    ):
        """Initialize the embeddings client.

        Args:
            model: Full model name, e.g. 'models/gemini-embedding-001'.
            api_key: Google AI Studio API key.
            batch_size: Number of texts per embed_content call. Gemini API
                accepts batches; 5 is a safe default that avoids 504s.
            max_retries: Number of attempts per batch on transient errors.
        """
        genai.configure(api_key=api_key, transport="rest")
        self.model = model
        self.batch_size = batch_size
        self.max_retries = max_retries

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents (used during ingestion).

        Batches internally and retries with exponential backoff.
        """
        all_embeddings: List[List[float]] = []
        total = len(texts)
        for i in range(0, total, self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (total + self.batch_size - 1) // self.batch_size
            embeddings = self._embed_with_retry(
                batch, task_type="retrieval_document",
                label=f"batch {batch_num}/{total_batches}",
            )
            all_embeddings.extend(embeddings)
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query (used during retrieval)."""
        return self._embed_with_retry(
            [text], task_type="retrieval_query", label="query",
        )[0]

    def _embed_with_retry(
        self, texts: List[str], task_type: str, label: str,
    ) -> List[List[float]]:
        """Call genai.embed_content with retry on transient errors.

        Raises the last exception if all retries fail.
        """
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                response = genai.embed_content(
                    model=self.model,
                    content=texts,
                    task_type=task_type,
                )
                # genai.embed_content returns:
                # - 1D list of floats when content is a single string
                # - 2D list (list of lists) when content is a list of strings
                embedding = response["embedding"]
                if texts and isinstance(embedding[0], (int, float)):
                    # Single string case — wrap in a list
                    return [list(embedding)]
                return [list(e) for e in embedding]
            except Exception as e:
                last_exc = e
                wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
                print(
                    f"  Embedding {label}: attempt {attempt + 1} "
                    f"failed ({type(e).__name__}: {e}). Retrying in {wait}s..."
                )
                time.sleep(wait)
        raise RuntimeError(
            f"Embedding {label} failed after {self.max_retries} attempts: "
            f"{last_exc}"
        ) from last_exc
