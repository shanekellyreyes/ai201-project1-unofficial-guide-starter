"""
query.py — Retrieve relevant chunks and generate a grounded answer via Groq.

Usage:
    python query.py "What do students think of the dining commons?"
"""

import os
import sys
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DB_DIR = "./chroma_db"
COLLECTION_NAME = "csueb_dining"
TOP_K = 4
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful assistant for the CSUEB Unofficial Dining Guide.
Answer the user's question using ONLY the information provided in the context below.
Do not use any outside knowledge.
If the context does not contain enough information to answer, respond with exactly:
"I don't have enough information on that."
Always be concise and cite which document your answer comes from."""

# Initialize clients once at module level
_client = chromadb.PersistentClient(path=DB_DIR)
_ef = embedding_functions.DefaultEmbeddingFunction()
_collection = _client.get_collection(COLLECTION_NAME, embedding_function=_ef)
_groq = Groq(api_key=os.environ["GROQ_API_KEY"])


def retrieve(question, k=TOP_K):
    results = _collection.query(query_texts=[question], n_results=k)
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": round(dist, 3)
        })
    return chunks


def ask(question):
    chunks = retrieve(question)

    # Build context string with source labels
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"

    response = _groq.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    answer = response.choices[0].message.content.strip()

    # Source attribution is guaranteed programmatically
    if "don't have enough information" in answer.lower():
        sources = []
    else:
        sources = sorted({c["source"] for c in chunks})

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What do students think of the dining commons?"
    result = ask(question)

    print(f"\nQ: {question}")
    print(f"\nANSWER:\n{result['answer']}")
    print(f"\nSOURCES: {result['sources']}")
    print("\nRETRIEVED CHUNKS:")
    for c in result["chunks"]:
        print(f"  {c['source']} (chunk {c['chunk_index']}, distance {c['distance']})")
