"""
rag.py — the RAG engine.

RAG = Retrieval-Augmented Generation. The LLM answers ONLY from text we retrieve
from your document, so it stays grounded (no hallucinating).

Pipeline (the 5 classic RAG steps):
  1. CHUNK   : split the document text into small overlapping pieces
  2. EMBED   : turn each chunk into a vector (list of numbers = its meaning)
  3. STORE   : keep those vectors in a FAISS index
  4. RETRIEVE: embed the user's question, find the most similar chunks
  5. ANSWER  : give those chunks + the question to the LLM -> grounded answer
"""

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # read the .env file into environment variables

# The embedding model. 'all-MiniLM-L6-v2' is small, fast, free, downloads ~80MB once.
# It turns any text into a 384-number vector.
_embedder = SentenceTransformer("all-MiniLM-L6-v2")


# ---------- STEP 1: CHUNK ----------
def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into ~chunk_size-character pieces, with overlap so we don't
    cut a sentence's meaning in half at the boundary."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # step back a little so chunks overlap
    # drop empty/whitespace-only chunks
    return [c.strip() for c in chunks if c.strip()]


# ---------- STEPS 2 & 3: EMBED + STORE ----------
def build_index(chunks):
    """Embed every chunk and put the vectors into a FAISS index for fast search."""
    # encode() returns one vector per chunk
    vectors = _embedder.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
    vectors = np.array(vectors, dtype="float32")
    dim = vectors.shape[1]  # 384 for this model
    index = faiss.IndexFlatL2(dim)  # L2 = straight-line distance between vectors
    index.add(vectors)  # store all chunk vectors
    return index


# ---------- STEP 4: RETRIEVE ----------
def retrieve(question, chunks, index, k=4):
    """Find the k chunks whose meaning is closest to the question.
    k is capped to the number of chunks available, and invalid (-1) hits are skipped."""
    k = min(k, len(chunks))
    q_vec = _embedder.encode([question], convert_to_numpy=True).astype("float32")
    distances, positions = index.search(q_vec, k)  # search the index
    # positions[0] holds the indexes of the top-k closest chunks (-1 means "no result")
    return [chunks[i] for i in positions[0] if i != -1]


# ---------- STEP 5: ANSWER ----------
def _llm_client_and_model():
    """Return an OpenAI-compatible client + model name, for OpenAI OR Ollama.
    (Ollama exposes an OpenAI-compatible API, so the same client works for both.)"""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        client = OpenAI(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama",  # Ollama ignores the key but the client requires a value
        )
        model = os.getenv("OLLAMA_MODEL", "llama3")
    else:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return client, model


def answer_question(question, context_chunks):
    """Ask the LLM to answer using ONLY the retrieved context."""
    context = "\n\n---\n\n".join(context_chunks)

    # Anti-hallucination + table-aware guardrail. We force the model to answer only
    # from the context, and give explicit rules for tabular data so it doesn't confuse
    # a grand-total row with an individual row, and compares values correctly.
    prompt = f"""You are a careful data assistant. Answer the QUESTION using ONLY the
CONTEXT below. Do not use outside knowledge. If the answer is not in the context,
say "I couldn't find that in the document."

Rules when the context looks like a table (rows of label: value pairs):
- Each row is one entity (e.g. one sales office). Read values per row.
- A row labelled "Total" / "Grand Total" is the SUM of all rows. It is NOT an
  individual office. Never report the Total as if it were one office's value.
- For "highest" / "lowest" / "which" questions: compare the relevant value across
  the individual rows (ignore the Total row) and name the row with the max/min.
- For "total" / "overall" questions: use the Total row if present, else sum the rows.
- Quote the exact number from the matching row.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    client, model = _llm_client_and_model()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # 0 = factual/consistent, not creative
        max_tokens=256,  # cap answer length -> faster responses
    )
    return resp.choices[0].message.content.strip()
