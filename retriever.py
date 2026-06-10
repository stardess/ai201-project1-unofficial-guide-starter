"""
retriever.py — Embedding, vector store, and retrieval.

Per planning.md:
  - Embedding model: all-MiniLM-L6-v2 (sentence-transformers, runs locally)
  - Vector store:    ChromaDB (persistent, local)
  - Top-k:          5

Public API:
    embed_and_store(chunks)          — embed chunks and upsert into ChromaDB
    retrieve(query, k=5)             — return top-k chunks with metadata + distances
    get_or_build_collection(chunks)  — convenience: load from disk or rebuild
"""

import os
from ingest import load_and_chunk_documents

import chromadb
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COLLECTION_NAME = "nd_rmp_reviews"
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Lazy singletons — initialised on first use
_model: SentenceTransformer | None = None
_client: chromadb.PersistentClient | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ---------------------------------------------------------------------------
# embed_and_store
# ---------------------------------------------------------------------------
def embed_and_store(chunks: list[dict]) -> None:
    """Embed every chunk and upsert into ChromaDB.

    Existing chunks with the same ID are overwritten, so this is safe
    to call multiple times (idempotent).

    Each ChromaDB document stores:
        document  — the chunk text (with professor/course prefix)
        metadata  — {source, professor, course, chunk_index}
        id        — "<source>_chunk_<index>"
    """
    model = _get_model()
    collection = _get_collection()

    print(f"Embedding {len(chunks)} chunks with {EMBEDDING_MODEL_NAME}...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_list=True)

    ids = [f"{c['source']}_chunk_{i}" for i, c in enumerate(chunks)]
    metadatas = [
        {
            "source": c["source"],
            "professor": c["professor"],
            "course": c["course"],
            "chunk_index": i,
        }
        for i, c in enumerate(chunks)
    ]

    # Upsert in one batch
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB collection '{COLLECTION_NAME}'.")


# ---------------------------------------------------------------------------
# retrieve
# ---------------------------------------------------------------------------
def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k most relevant chunks for a query.

    Returns a list of dicts, each with:
        text        — chunk text
        source      — source filename
        professor   — professor name
        course      — course code
        distance    — cosine distance (lower = more similar; range 0–2 for cosine)
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query], convert_to_list=True)[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text": text,
                "source": meta.get("source", ""),
                "professor": meta.get("professor", ""),
                "course": meta.get("course", ""),
                "distance": round(dist, 4),
            }
        )
    return chunks


# ---------------------------------------------------------------------------
# get_or_build_collection
# ---------------------------------------------------------------------------
def get_or_build_collection(docs_dir: str | None = None) -> None:
    """Load ChromaDB from disk if already populated; otherwise build from scratch."""
    collection = _get_collection()
    if collection.count() > 0:
        print(f"ChromaDB already contains {collection.count()} chunks. Skipping re-embed.")
        return
    chunks = load_and_chunk_documents(docs_dir) if docs_dir else load_and_chunk_documents()
    embed_and_store(chunks)


# ---------------------------------------------------------------------------
# CLI: test retrieval with evaluation-plan queries
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Build (or reuse) the collection
    get_or_build_collection()

    test_queries = [
        "What is Katherine Walden's grading system in CDT30010?",
        "How hard are Peter Bui's exams in Systems Programming?",
        "Does Daniel Cedre require office hours to pass CSE10001?",
        "What do students say about Tijana Milenkovic's grading strictness?",
        "Is Ramzi Bualuan recommended for students with no prior CS experience?",
    ]

    for query in test_queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)
        results = retrieve(query, k=5)
        for rank, r in enumerate(results, 1):
            print(
                f"\n  [{rank}] distance={r['distance']:.4f}  "
                f"| {r['professor']} | {r['course']} | {r['source']}"
            )
            # Print first 200 chars of chunk text
            preview = r["text"].replace("\n", " ")[:220]
            print(f"       {preview}...")
