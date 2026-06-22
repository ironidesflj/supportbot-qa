"""Seed the Qdrant knowledge base with sample documents.

Usage:
    python3 seed_kb.py

Ingests all .md files from docs/sample_kb/ into Qdrant. Useful for:
  - Populating the KB before running `pytest eval/tests/`
  - Quick manual testing of the chat endpoint
  - Demo preparation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.rag.ingestion import IngestionPipeline

SAMPLE_KB_DIR = Path(__file__).parent / "docs" / "sample_kb"


def main():
    """Ingest all sample documents into Qdrant."""
    if not SAMPLE_KB_DIR.exists():
        print(f"ERROR: sample KB directory not found: {SAMPLE_KB_DIR}")
        sys.exit(1)

    md_files = sorted(SAMPLE_KB_DIR.glob("*.md"))
    if not md_files:
        print(f"ERROR: no .md files found in {SAMPLE_KB_DIR}")
        sys.exit(1)

    print(f"Found {len(md_files)} documents to ingest:")
    for f in md_files:
        print(f"  - {f.name}")
    print()

    pipeline = IngestionPipeline()
    total_chunks = 0
    for f in md_files:
        try:
            chunks = pipeline.ingest(str(f))
            print(f"  OK  {f.name}: {chunks} chunks added")
            total_chunks += chunks
        except Exception as e:
            print(f"  FAIL {f.name}: {e}")
            sys.exit(1)

    print(f"\nDone. Total chunks ingested: {total_chunks}")


if __name__ == "__main__":
    main()
