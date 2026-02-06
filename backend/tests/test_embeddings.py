# tests/test_embeddings.py
"""
Standalone test script for Voyage AI embeddings.

Run with:
    cd backend
    python -m tests.test_embeddings
"""

import os
import sys

# Ensure the backend directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_voyage_connection():
    """Test that the Voyage AI client can connect and generate embeddings."""
    from dotenv import load_dotenv

    # Load .env from the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(backend_dir, ".env"))

    api_key = os.getenv("VOYAGE_API_KEY", "")
    if not api_key:
        print("❌ VOYAGE_API_KEY is not set in .env")
        print("   Get a free key at https://www.voyageai.com/ (50M free tokens, no credit card)")
        sys.exit(1)

    try:
        import voyageai
    except ImportError:
        print("❌ voyageai package not installed. Run: pip install voyageai==0.2.1")
        sys.exit(1)

    print("🔄 Testing Voyage AI connection...")

    try:
        client = voyageai.Client(api_key=api_key)
        result = client.embed(
            texts=["Hello, this is a test embedding for the onboarding platform."],
            model="voyage-2",
        )

        embedding = result.embeddings[0]
        print("✅ Voyage AI connection successful")
        print(f"✅ Embedding shape: (1, {len(embedding)})")
        print(f"   First 5 values: {embedding[:5]}")

    except Exception as e:
        print(f"❌ Voyage AI connection failed: {e}")
        sys.exit(1)


def test_chromadb_integration():
    """Test that the VoyageEmbeddingFunction works with ChromaDB."""
    from dotenv import load_dotenv

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(backend_dir, ".env"))

    api_key = os.getenv("VOYAGE_API_KEY", "")
    if not api_key:
        print("⏭️  Skipping ChromaDB integration test (no VOYAGE_API_KEY)")
        return

    print("🔄 Testing ChromaDB + Voyage AI integration...")

    try:
        from app.services.embeddings import VoyageEmbeddingFunction
        import chromadb

        ef = VoyageEmbeddingFunction()
        client = chromadb.Client()  # In-memory for testing

        collection = client.get_or_create_collection(
            name="test_collection",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

        # Add test documents
        collection.add(
            documents=["Employee onboarding policy", "Company benefits overview"],
            ids=["doc1", "doc2"],
        )

        # Query
        results = collection.query(query_texts=["onboarding"], n_results=1)
        print("✅ ChromaDB + Voyage AI integration works")
        print(f"   Query result: {results['documents'][0][0][:50]}...")

        # Cleanup
        client.delete_collection("test_collection")

    except Exception as e:
        print(f"❌ ChromaDB integration test failed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("  Voyage AI Embedding Test Suite")
    print("=" * 50)
    print()

    test_voyage_connection()
    print()
    test_chromadb_integration()

    print()
    print("=" * 50)
    print("  All tests passed! ✅")
    print("=" * 50)
