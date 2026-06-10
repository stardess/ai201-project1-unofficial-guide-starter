"""
ingest.py — Document ingestion and chunking pipeline.

Loads RMP review .txt files from documents/, parses each review block,
and splits them into chunks per the spec in planning.md:
  - Chunk size:  500 characters
  - Overlap:     50 characters
  - Metadata prepended: professor name + course code on every chunk

Each returned chunk dict has the keys:
  text       — the chunk text (with professor/course prefix)
  source     — the original filename (e.g. "prof_Bui_rmp.txt")
  professor  — professor full name (e.g. "Peter Bui")
  course     — course code of the review (e.g. "CSE20289"), or "Unknown"
"""

import os
import re

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _split_with_overlap(text: str, size: int, overlap: int) -> list[str]:
    """Split text into chunks of `size` characters with `overlap` overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if len(c) > 0]


def _parse_professor_name(header_line: str) -> str:
    """Extract professor name from the first line of a file.

    Expected format: 'Prof: First Last, rate: X/5'
    or               'prof: First Last, rate: X/5'
    """
    match = re.search(r"[Pp]rof(?:essor)?:?\s+(.+?),\s*rate", header_line)
    if match:
        return match.group(1).strip()
    return "Unknown Professor"


def _parse_course(review_block: str) -> str:
    """Extract the course code from a review block.

    Looks for a line starting with 'Course:' followed by a code.
    """
    match = re.search(r"^Course:\s*(\S+)", review_block, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown"


def _clean_review_block(block: str) -> str:
    """Strip blank lines, trailing whitespace, and leftover RTF/HTML artifacts."""
    # Remove any HTML entities (shouldn't be present but guard anyway)
    block = re.sub(r"&[a-zA-Z]+;", " ", block)
    block = re.sub(r"&#\d+;", " ", block)
    # Collapse multiple blank lines into one
    block = re.sub(r"\n{3,}", "\n\n", block)
    return block.strip()


def load_and_chunk_documents(docs_dir: str = DOCS_DIR) -> list[dict]:
    """Load all .txt files in docs_dir and return a flat list of chunk dicts.

    Each chunk dict:
        {
            "text":      "<Professor | Course> <chunk text>",
            "source":    "prof_Bui_rmp.txt",
            "professor": "Peter Bui",
            "course":    "CSE20289",
        }
    """
    all_chunks = []

    txt_files = sorted(
        f for f in os.listdir(docs_dir) if f.endswith(".txt") and f != ".gitkeep"
    )

    for filename in txt_files:
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, encoding="utf-8") as fh:
            raw = fh.read()

        # First non-blank line is the professor header
        lines = raw.splitlines()
        header_line = next((l for l in lines if l.strip()), "")
        professor = _parse_professor_name(header_line)

        # Split the file into individual review blocks on '---' separators
        review_blocks = re.split(r"\n---+\n", raw)

        for block in review_blocks:
            block = _clean_review_block(block)
            if not block:
                continue

            # Skip the file header block (contains "Prof:" and "Source:" but no opinion)
            if re.match(r"[Pp]rof(?:essor)?:", block) and "Source:" in block and len(block) < 200:
                continue

            course = _parse_course(block)

            # Build the prefix that will be prepended to every chunk from this review
            prefix = f"[Professor: {professor} | Course: {course}]\n"

            # If the whole block fits in one chunk, emit it directly
            if len(prefix) + len(block) <= CHUNK_SIZE:
                all_chunks.append(
                    {
                        "text": prefix + block,
                        "source": filename,
                        "professor": professor,
                        "course": course,
                    }
                )
            else:
                # Apply character-level chunking with overlap
                sub_chunks = _split_with_overlap(block, CHUNK_SIZE - len(prefix), CHUNK_OVERLAP)
                for sub in sub_chunks:
                    if sub.strip():
                        all_chunks.append(
                            {
                                "text": prefix + sub,
                                "source": filename,
                                "professor": professor,
                                "course": course,
                            }
                        )

    return all_chunks


if __name__ == "__main__":
    import random

    chunks = load_and_chunk_documents()

    print(f"\nTotal chunks: {len(chunks)}\n")
    print("=" * 60)

    # Print 5 random chunks for inspection
    sample = random.sample(chunks, min(5, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"--- Chunk {i} ---")
        print(f"Source:    {chunk['source']}")
        print(f"Professor: {chunk['professor']}")
        print(f"Course:    {chunk['course']}")
        print(f"Length:    {len(chunk['text'])} chars")
        print(f"Text:\n{chunk['text']}")
        print()
