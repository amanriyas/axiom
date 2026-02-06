# app/services/rag.py
"""RAG (Retrieval-Augmented Generation) service — ChromaDB vector store for policy documents."""

import os
from typing import Optional

from app.config import settings

# ChromaDB persistence directory
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chromadb")

# Lazy-loaded ChromaDB client
_chroma_client = None
_collection = None


def _get_collection():
    """Get or create the ChromaDB collection (lazy initialization)."""
    global _chroma_client, _collection

    if _collection is not None:
        return _collection

    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        os.makedirs(CHROMA_DIR, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _chroma_client.get_or_create_collection(
            name="policy_documents",
            metadata={"hnsw:space": "cosine"},
        )
        return _collection
    except ImportError:
        print("⚠️  ChromaDB not installed. RAG features will use mock mode.")
        return None
    except Exception as e:
        print(f"⚠️  ChromaDB initialization failed: {e}. RAG features will use mock mode.")
        return None


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        print("⚠️  PyMuPDF not installed. Returning empty text.")
        return ""
    except Exception as e:
        print(f"⚠️  Error extracting PDF text: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for embedding."""
    if not text.strip():
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap

    return chunks


def embed_policy(policy_id: int, file_path: str, title: str) -> int:
    """
    Extract text from a policy PDF, chunk it, and store embeddings in ChromaDB.

    Returns the number of chunks embedded.
    """
    collection = _get_collection()

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    if collection is None:
        # Mock mode — just return count
        print(f"📄 [Mock RAG] Would embed {len(chunks)} chunks for policy '{title}'")
        return len(chunks)

    # Create IDs and metadata for each chunk
    ids = [f"policy_{policy_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"policy_id": policy_id, "title": title, "chunk_index": i} for i in range(len(chunks))]

    # Remove existing chunks for this policy (re-embedding)
    try:
        existing = collection.get(where={"policy_id": policy_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    # Add new chunks
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    return len(chunks)


def query_policies(query: str, n_results: int = 5) -> list[dict]:
    """
    Query the policy vector store for relevant context.

    Returns a list of dicts with { text, policy_id, title, score }.
    """
    collection = _get_collection()

    if collection is None or collection.count() == 0:
        return _mock_query(query)

    try:
        results = collection.query(query_texts=[query], n_results=n_results)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "text": doc,
                "policy_id": meta.get("policy_id"),
                "title": meta.get("title", "Unknown"),
                "score": 1 - dist,  # Convert distance to similarity
            }
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]
    except Exception as e:
        print(f"⚠️  RAG query failed: {e}")
        return _mock_query(query)


def _mock_query(query: str) -> list[dict]:
    """Return mock policy context for demos."""
    return [
        {
            "text": (
                "Company Policy: All new employees must complete orientation within their first week. "
                "Equipment will be provisioned by IT within 48 hours of the start date. "
                "Managers should schedule a 1:1 meeting within the first 3 days."
            ),
            "policy_id": 0,
            "title": "Mock Company Policy",
            "score": 0.85,
        }
    ]


def delete_policy_embeddings(policy_id: int) -> bool:
    """Remove all embeddings for a given policy."""
    collection = _get_collection()
    if collection is None:
        return True

    try:
        existing = collection.get(where={"policy_id": policy_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
        return True
    except Exception:
        return False
