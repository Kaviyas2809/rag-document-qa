"""
loader.py — read raw text out of a file.

Supports:
  .pdf  -> extract text with pypdf
  .txt / .md -> read as-is
  .xlsx / .csv -> turn each ROW into a readable sentence (so tables work with RAG)

Why turn Excel rows into sentences? RAG works on text. A row like
  Zone=SOUTH, Office=AP, Collection=5.59
reads naturally as: "Zone: SOUTH | Office: AP | Collection: 5.59".
Then the embedder can match a question like "collection for AP" to that row.
"""

import os


def load_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return _load_pdf(path)
    if ext in (".txt", ".md"):
        return _load_text(path)
    if ext in (".xlsx", ".xls", ".csv"):
        return _load_table(path)
    raise ValueError(f"Unsupported file type: {ext}. Use pdf, txt, md, csv or xlsx.")


def _load_pdf(path):
    from pypdf import PdfReader
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _load_table(path):
    import pandas as pd
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    # Convert each row to "Col: val | Col: val | ..." so it reads like a sentence.
    lines = []
    for _, row in df.iterrows():
        parts = [f"{col}: {row[col]}" for col in df.columns]
        lines.append(" | ".join(parts))
    return "\n".join(lines)
