
from pathlib import Path
from uuid import uuid4

import chromadb
from sentence_transformers import SentenceTransformer


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Persistent ChromaDB storage
client = chromadb.PersistentClient(
    path=str(BASE_DIR / "data" / "chroma_db")
)

# Create or connect to the document collection
collection = client.get_or_create_collection(
    name="knowledge_documents",
    metadata={"hnsw:space": "cosine"}
)

# Load the embedding model using PyTorch
print("Loading Sentence Transformer model...")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("Embedding model loaded successfully!")


def store_chunks(chunks: list[dict], source: str) -> int:
    """Convert document chunks into embeddings and store them."""

    if not chunks:
        return 0

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False
    ).tolist()

    ids = [str(uuid4()) for _ in chunks]

    metadatas = [
        {
            "source": source,
            "page": chunk["page"],
            "chunk_id": chunk["chunk_id"]
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_chunks(query: str, top_k: int = 3) -> list[dict]:
    """Find document chunks semantically related to a question."""

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_embedding = model.encode(
        query,
        convert_to_numpy=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total_chunks),
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for i, document in enumerate(results["documents"][0]):
        matches.append({
            "text": document,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return matches
