# app/services/embeddings.py
"""Voyage AI embedding provider for ChromaDB vector store.

Voyage AI offers high-quality embeddings with 50M free tokens (no credit card required).
Used as the primary embedding function for the RAG pipeline.

Docs: https://docs.voyageai.com/
"""

import os
import time
from typing import List

from app.config import settings


class VoyageEmbeddingFunction:
    """ChromaDB-compatible embedding function using Voyage AI.

    Usage:
        ef = VoyageEmbeddingFunction()
        embeddings = ef(["Hello world", "Another sentence"])
    """

    def __init__(self, api_key: str = "", model: str = ""):
        """Initialize the Voyage AI client.

        Args:
            api_key: Voyage AI API key. Falls back to VOYAGE_API_KEY env var / settings.
            model:   Embedding model name. Falls back to settings.VOYAGE_EMBEDDING_MODEL.
        """
        import voyageai

        resolved_key = api_key or settings.VOYAGE_API_KEY or os.getenv("VOYAGE_API_KEY", "")
        if not resolved_key:
            raise ValueError(
                "VOYAGE_API_KEY is not set. "
                "Get a free key at https://www.voyageai.com/ (50M free tokens, no credit card)."
            )

        self.client = voyageai.Client(api_key=resolved_key)
        self.model = model or settings.VOYAGE_EMBEDDING_MODEL or "voyage-2"
        self._max_retries = 3
        self._retry_delay = 1.0  # seconds

    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Compatible with ChromaDB's EmbeddingFunction protocol.
        Includes retry logic for transient API failures.

        Args:
            input: List of text strings to embed.

        Returns:
            List of embedding vectors (list of floats).
        """
        last_error = None

        for attempt in range(1, self._max_retries + 1):
            try:
                result = self.client.embed(texts=input, model=self.model)
                return result.embeddings
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    wait = self._retry_delay * attempt
                    print(f"⚠️  Voyage AI embed attempt {attempt} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)

        raise RuntimeError(
            f"Voyage AI embedding failed after {self._max_retries} attempts: {last_error}"
        )


def get_voyage_embedding_function() -> VoyageEmbeddingFunction:
    """Factory function to create a VoyageEmbeddingFunction.

    Returns:
        VoyageEmbeddingFunction instance ready for use with ChromaDB.

    Raises:
        ValueError: If VOYAGE_API_KEY is not configured.
    """
    return VoyageEmbeddingFunction()


def get_langchain_voyage_embeddings():
    """Get a LangChain-compatible Voyage AI embedding model.

    Useful for LangChain pipelines and document loaders.

    Returns:
        VoyageAIEmbeddings instance for LangChain.
    """
    from langchain_voyageai import VoyageAIEmbeddings

    api_key = settings.VOYAGE_API_KEY or os.getenv("VOYAGE_API_KEY", "")
    if not api_key:
        raise ValueError("VOYAGE_API_KEY is not set.")

    return VoyageAIEmbeddings(
        voyage_api_key=api_key,
        model=settings.VOYAGE_EMBEDDING_MODEL or "voyage-2",
    )
