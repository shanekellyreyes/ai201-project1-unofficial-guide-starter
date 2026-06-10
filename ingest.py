"""
ingest.py — Load, clean, chunk, and embed documents into ChromaDB.

Run this once before using the app:
    python ingest.py
"""

import os
import re
import glob
import chromadb
from chromadb.utils import embedding_functions

DOCS_DIR = "documents"
DB_DIR = "./chroma_db"
COLLECTION_NAME = "csueb_dining"

CHUNK_SIZE = 400    # characters (~80-100 words) — fits short Yelp/Reddit reviews
OVERLAP = 80        # characters — carries restaurant names across chunk boundaries


def clean(text):
    """Remove HTML, decode entities, normalize whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&amp;", "&")
                .replace("&nbsp;", " ")
                .replace("&#39;", "'")
                .replace("&quot;", '"'))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text):
    """
    Paragraph-aware packing. Split on blank lines first to keep whole
    reviews intact. Hard-split only when a paragraph exceeds CHUNK_SIZE.
    """
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, buf = [], ""

    for p in paras:
        if len(p) > CHUNK_SIZE:
            if buf:
                chunks.append(buf)
                buf = ""
            start = 0
            while start < len(p):
                chunks.append(p[start:start + CHUNK_SIZE])
                start += CHUNK_SIZE - OVERLAP
        elif len(buf) + len(p) + 2 <= CHUNK_SIZE:
            buf = (buf + "\n\n" + p).strip()
        else:
            chunks.append(buf)
            buf = p

    if buf:
        chunks.append(buf)

    return [c for c in chunks if len(c.strip()) > 20]


def main():
    # Set up ChromaDB
    client = chromadb.PersistentClient(path=DB_DIR)

    # Reset collection so re-running is safe
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    ef = embedding_functions.DefaultEmbeddingFunction()  # all-MiniLM-L6-v2
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    ids, texts, metadatas = [], [], []
    total_chunks = 0

    for path in sorted(glob.glob(os.path.join(DOCS_DIR, "*.txt"))):
        source = os.path.basename(path)
        raw = open(path, encoding="utf-8").read()
        cleaned = clean(raw)
        chunks = chunk_text(cleaned)

        for i, chunk in enumerate(chunks):
            ids.append(f"{source}::{i}")
            texts.append(chunk)
            metadatas.append({"source": source, "chunk_index": i})
            total_chunks += 1

        print(f"  {source}: {len(chunks)} chunks")

    collection.add(ids=ids, documents=texts, metadatas=metadatas)

    print(f"\nDone! {len(set(m['source'] for m in metadatas))} documents -> {total_chunks} total chunks")
    print(f"Stored in ChromaDB at: {DB_DIR}")

    # Print 5 sample chunks for inspection
    print("\n--- 5 sample chunks ---")
    for text, meta in list(zip(texts, metadatas))[:5]:
        print(f"\n[{meta['source']} | chunk {meta['chunk_index']}]")
        print(text)
        print("-" * 40)


if __name__ == "__main__":
    main()
