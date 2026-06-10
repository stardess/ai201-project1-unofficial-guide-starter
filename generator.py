"""
generator.py — Grounded response generation using Groq + retrieved chunks.

Per planning.md:
  - LLM:    Groq llama-3.3-70b-versatile
  - Grounding: system prompt hard-restricts answers to retrieved context only
  - Attribution: source filenames are appended programmatically after generation

Public API:
    ask(question, k=5) -> {"answer": str, "sources": list[str], "chunks": list[dict]}
"""

import os
from dotenv import load_dotenv
from groq import Groq
from retriever import get_or_build_collection, retrieve

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful assistant for Notre Dame students looking up professor reviews from Rate My Professors.

STRICT RULES — you must follow these without exception:
1. Answer ONLY using information from the provided student reviews below. Do not use any outside knowledge.
2. If the reviews do not contain enough information to answer the question, respond with exactly: "I don't have enough information in the available reviews to answer that."
3. Never invent, assume, or extrapolate facts not stated in the reviews.
4. When you reference a review, include the professor's name and course code as they appear in the review context.
5. Keep your answer concise and focused on what students actually said."""


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Review {i} | Source: {chunk['source']} | {chunk['professor']} | {chunk['course']}]\n{chunk['text']}")
    return "\n\n".join(parts)


def _deduplicate_sources(chunks: list[dict]) -> list[str]:
    """Return unique source filenames in retrieval-rank order."""
    seen = set()
    sources = []
    for chunk in chunks:
        s = chunk["source"]
        if s not in seen:
            seen.add(s)
            sources.append(s)
    return sources


def ask(question: str, k: int = 5) -> dict:
    """Run end-to-end: retrieve chunks → generate grounded answer.

    Returns:
        {
            "answer":  str   — LLM response grounded in retrieved chunks,
            "sources": list  — deduplicated source filenames (programmatic),
            "chunks":  list  — raw retrieved chunk dicts for inspection,
        }
    """
    # Ensure the vector store is populated
    get_or_build_collection()

    # Retrieve top-k relevant chunks
    chunks = retrieve(question, k=k)

    # If no chunks retrieved (shouldn't happen, but guard anyway)
    if not chunks:
        return {
            "answer": "I don't have enough information in the available reviews to answer that.",
            "sources": [],
            "chunks": [],
        }

    context = _build_context(chunks)

    user_message = f"""Using only the student reviews below, answer this question:

QUESTION: {question}

STUDENT REVIEWS:
{context}

Remember: only use what is stated in the reviews above. If the reviews don't answer the question, say so."""

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,   # low temperature = more faithful to context
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()

    # Source attribution is programmatically guaranteed — never depends on LLM
    sources = _deduplicate_sources(chunks)

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_queries = [
        # In-scope queries (should answer from documents)
        "What is Katherine Walden's grading system in CDT30010?",
        "How hard are Peter Bui's exams in Systems Programming?",
        "Does Daniel Cedre require office hours to pass CSE10001?",
        # Out-of-scope query (should decline)
        "What is the best restaurant near Notre Dame campus?",
    ]

    for q in test_queries:
        print("\n" + "=" * 70)
        print(f"Q: {q}")
        print("=" * 70)
        result = ask(q)
        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nSOURCES: {', '.join(result['sources'])}")
