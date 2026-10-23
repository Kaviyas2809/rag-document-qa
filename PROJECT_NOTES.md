# RAG Mini Project — Complete Notes

_Document Q&A using Retrieval-Augmented Generation (RAG). Free, local, no paid API._
_Author: Kaviya Dharshini S — D&AI, TVS Motor._

---

## 1. One-line summary
Upload a PDF or Excel/CSV file, ask a question in plain English, and the app answers
using ONLY the content of that document — running entirely on a free local AI model,
so no data leaves the machine and there is no API cost.

---

## 2. What problem it solves
- Business info is locked inside PDFs and Excel files (reports, policies, specs).
- People read through files manually, or keep asking the data team.
- This lets anyone self-serve answers from a document in plain English.

---

## 3. What RAG is (how to explain simply)
RAG = Retrieval-Augmented Generation. It is like an OPEN-BOOK EXAM for the AI:
- A normal LLM answers from memory and can hallucinate (make things up).
- A RAG app FIRST finds the relevant text in the document, then answers only from that.
=> answers are grounded and trustworthy.

The 5 RAG steps (this whole project is these 5 steps):
  1. CHUNK   - split the document into small pieces
  2. EMBED   - turn each piece into a vector (numbers that capture meaning)
  3. STORE   - keep the vectors in a fast search index (FAISS)
  4. RETRIEVE- turn the question into a vector, find the most similar pieces
  5. ANSWER  - the LLM answers using ONLY those retrieved pieces

Flow:
  Upload file -> read text -> chunk -> embed -> store in FAISS
  Question -> embed -> FAISS finds closest chunks -> LLM answers from those chunks -> shown in UI

---

## 4. The model we use
- Model: **Qwen 2.5 - 0.5B Instruct** (small, 0.5 billion parameters), open-source by Alibaba.
- In Ollama it is named: **qwen-rag:latest** (~491 MB).
- Runs locally via **Ollama** — free, no GPU needed, nothing sent to cloud.
- Original file: `qwen2.5-0.5b-instruct-q4_k_m.gguf` (downloaded from Hugging Face, imported into
  Ollama with a Modelfile).
- Embedding model (separate, for the vectors): `all-MiniLM-L6-v2` (sentence-transformers, local, ~80 MB,
  produces 384-number vectors).

---

## 5. The files (what each one does)

### loader.py — "read the file"
Pulls raw TEXT out of a file.
- PDF  -> extract text with pypdf
- txt / md -> read directly
- xlsx / xls / csv -> turn EACH ROW into a sentence like "Zone: SOUTH | Office: AP | Collection: 5.59"
  (RAG needs text, so a table row is rendered as readable text). Needs pandas + openpyxl (.xlsx) + xlrd (.xls).

### rag.py — "the brain" (the core RAG engine)
- chunk_text()  : splits text into ~500-char chunks with 100-char overlap (so meaning isn't cut at edges).
- build_index() : embeds each chunk with all-MiniLM-L6-v2, stores vectors in a FAISS IndexFlatL2.
- retrieve()    : embeds the question, FAISS returns the top-k most similar chunks (k capped to #chunks).
- answer_question(): sends the retrieved chunks + question to the LLM with a STRICT prompt:
    "answer ONLY from this context; if not present, say you couldn't find it" (anti-hallucination).
    Also has TABLE RULES (don't treat a Total row as one office; compare per-row for highest/lowest).
    temperature=0 (factual), max_tokens=256 (faster).
- _llm_client_and_model(): switches between Ollama (free/local) and OpenAI via the .env setting. Ollama
    exposes an OpenAI-compatible API, so the same client code works for both.

### main.py — command-line version
Load a file, build the index once, then a loop: type a question -> get an answer. Proves the engine works.

### app.py — web UI (Streamlit)
- Upload button (pdf/xlsx/xls/csv/txt/md).
- On upload: loader -> chunk -> build_index once (kept in session_state).
- Question box -> retrieve top 5 chunks -> answer -> shows Q&A history on the page.
- Run with: `streamlit run app.py`  (opens http://localhost:8501).

### supporting files
- requirements.txt : all libraries (sentence-transformers, faiss-cpu, pypdf, pandas, openpyxl, xlrd,
  openai, python-dotenv, streamlit).
- .env             : active config (LLM_PROVIDER=ollama, OLLAMA_MODEL=qwen-rag). NOT pushed to GitHub.
- .env.example     : template (safe to publish).
- .gitignore       : excludes .env (secrets), venv/, *.gguf (big model), __pycache__.
- Modelfile        : `FROM ./qwen0.5b.gguf` — how the GGUF was imported into Ollama.
- data/            : sample files (sample_report.md prose, sample_sales.csv table) — fake data, safe.

---

## 6. Tech stack (all free / open-source)
| Purpose            | Tool                         |
|--------------------|------------------------------|
| Embeddings (meaning)| sentence-transformers (all-MiniLM-L6-v2) |
| Vector search      | FAISS (faiss-cpu)            |
| Read PDF           | pypdf                        |
| Read Excel/CSV     | pandas, openpyxl, xlrd       |
| Local LLM          | Ollama (Qwen 2.5 0.5B)       |
| Web UI             | Streamlit                    |
| Config/secrets     | python-dotenv                |

---

## 7. Problems faced & how we solved them (good to mention — shows real work)
1. Ollama model wouldn't download: diagnosed the laptop security software throttled Ollama's blob CDN to
   ~143 B/s (99h+ ETA). FIX: downloaded the GGUF from Hugging Face instead (~1.7 MB/s, needed
   `curl --ssl-no-revoke` to pass the corporate TLS revocation block), then `ollama create` + Modelfile.
2. Wrong answer on a big table (it reported the grand Total 144.53 as one zone's value). FIX: added
   table-aware rules to the prompt (ignore Total row; compare per-row for highest/lowest) and raised the
   number of retrieved chunks.
3. Old .xls file failed: missing dependency. FIX: installed xlrd.
4. Slow responses: local CPU model. FIX: fewer chunks (k=5), max_tokens=256, OLLAMA_KEEP_ALIVE=30m.

---

## 8. Strengths & limits (be honest in the demo)
STRONG: finding/summarizing facts in TEXT docs (reports, policies, resumes, specs); lookups on small tables.
LIMITS: the small 0.5B model is weak at math/ranking across LARGE number tables ("which of 40 rows is
  highest"). For that: use a bigger free model (Qwen 2.5 3B / Llama 3.2 3B) OR an NL-to-SQL approach for
  pure data tables. Local CPU => answers take a few seconds (trade-off for free + private + offline).

---

## 9. Good demo files & questions
- A text report / leave policy PDF: "summarize this", "how many casual leaves are allowed?".
- Your resume (PDF): "what are her skills?", "which certifications?".
- A small CSV (~10-15 rows): lookup questions like "what is the billing for KAR?".
- AVOID live: "which of 40 rows is highest / total of everything" on a big table (small-model weakness).

---

## 10. How to run
```
cd C:\Users\kaviya.dharshini\rag-document-qa
venv\Scripts\activate
# Web UI:
streamlit run app.py          # then open http://localhost:8501
# OR command line:
python main.py --file data/sample_sales.csv
```
(Ollama must be running, and the qwen-rag model present: check with `ollama list`.)

---

## 11. Manager Q&A cheat-sheet
- "Does it hallucinate?" -> No; it answers only from retrieved document text, else says it couldn't find it.
- "Is it free?" -> Yes; local Qwen 2.5 via Ollama, no API cost.
- "Does data leave the machine?" -> No; everything runs locally/offline.
- "Where did the RAG certification apply?" -> This is the hands-on implementation: embeddings, vector
  search, retrieval, grounded generation.
- "Limits / next steps?" -> Bigger model for number reasoning; voice + NL-to-SQL agent for data questions.
