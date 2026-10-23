# RAG Document Q&A

Ask questions in plain English about your own documents (PDF, Excel/CSV, text) and
get answers grounded **only** in the document — no hallucination. A hands-on
implementation of **Retrieval-Augmented Generation (RAG)**.

Built to demonstrate the RAG pattern end to end: chunking, embeddings, vector
search (FAISS), and grounded answer generation with an LLM.

## What it does
1. **Load** a document (`.pdf`, `.xlsx`, `.csv`, `.txt`, `.md`)
2. **Chunk** it into small overlapping pieces
3. **Embed** each chunk into a vector with a local sentence-transformer model
4. **Store** the vectors in a FAISS index
5. **Retrieve** the chunks most similar to your question
6. **Answer** using an LLM, constrained to the retrieved context

```
Document ──chunk──► pieces ──embed──► vectors ──► FAISS index
                                                     │
Question ──embed──► vector ──search──► top-k chunks ─┘
                                        │
                                        ▼
                         LLM answers using ONLY those chunks
```

## Tech
- `sentence-transformers` (all-MiniLM-L6-v2) — local, free embeddings
- `faiss-cpu` — vector similarity search
- `pypdf`, `pandas`/`openpyxl` — document loading
- OpenAI **or** Ollama (free, local) for the LLM — switchable via `.env`

## Setup
```bash
# 1. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. configure the LLM
copy .env.example .env         # Windows   (cp on Mac/Linux)
# edit .env: set LLM_PROVIDER=openai and your OPENAI_API_KEY
#            OR  LLM_PROVIDER=ollama  (after: ollama pull llama3)
```

## Getting the local LLM (free, via Ollama)

This project uses a local model through Ollama — no API key, no cost. The model file
is not committed to git (too large). To set it up once:

```bash
# Option A — normal Ollama pull (if your network allows it)
ollama pull llama3.2
# then set OLLAMA_MODEL=llama3.2 in .env

# Option B — if `ollama pull` is blocked/throttled on your machine, download the
# GGUF from Hugging Face instead and import it locally:
curl -L --ssl-no-revoke -o qwen0.5b.gguf ^
  https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf
ollama create qwen-rag -f Modelfile
# then set OLLAMA_MODEL=qwen-rag in .env
```

## Run
```bash
# Ask a prose report (PDF-style)
python main.py --file data/sample_report.md

# Ask a table (Excel/CSV)
python main.py --file data/sample_sales.csv
```

### Example
```
You: what was the total collection for the month?
Bot: Total collection for October 2026 was 144.53 crore, which was 100% of plan.

You: which office had the highest collection?
Bot: WB had the highest collection at 12.27 crore.
```

## Project structure
```
rag-document-qa/
├── main.py            # entry point + chat loop
├── loader.py          # read PDF / Excel / CSV / text into raw text
├── rag.py             # chunk, embed, index, retrieve, answer (the RAG engine)
├── requirements.txt
├── .env.example       # LLM config template
└── data/              # sample documents (fake data, safe to share)
```

## What I learned
- How embeddings turn meaning into vectors, and how vector search finds relevant text
- Why chunking + overlap matters for retrieval quality
- How a grounding prompt ("answer only from this context") controls hallucination
- Making tabular (Excel) data work with RAG by rendering rows as sentences
