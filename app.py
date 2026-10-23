"""
app.py — a simple web UI for the RAG Document Q&A, built with Streamlit.

Run it with:
    streamlit run app.py

Then your browser opens a page where you can:
  1. Upload a PDF / Excel / CSV / text file
  2. Type questions about it
  3. See grounded answers on screen

It reuses the same RAG engine (loader.py + rag.py) as the command-line version.
"""

import os
import tempfile
import streamlit as st

from loader import load_file
from rag import chunk_text, build_index, retrieve, answer_question

# ---- page setup ----
st.set_page_config(page_title="Document Q&A (RAG)", page_icon="📄", layout="centered")
st.title("📄 Document Q&A")
st.caption(
    "Upload a PDF, Excel, or CSV and ask questions about it. Answers come only from the document."
)

# ---- session state keeps the index between questions ----
if "chunks" not in st.session_state:
    st.session_state.chunks = None
    st.session_state.index = None
    st.session_state.filename = None
    st.session_state.history = []  # list of (question, answer)

# ---- STEP 1: upload a file ----
uploaded = st.file_uploader(
    "Upload a document",
    type=["pdf", "xlsx", "xls", "csv", "txt", "md"],
)

# When a new file is uploaded, build the RAG index for it (once).
if uploaded is not None and uploaded.name != st.session_state.filename:
    with st.spinner(f"Reading and indexing '{uploaded.name}'..."):
        # save the uploaded bytes to a temp file so loader.py can read it
        suffix = os.path.splitext(uploaded.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = tmp.name
        try:
            text = load_file(tmp_path)
            chunks = chunk_text(text)
            index = build_index(chunks)
            st.session_state.chunks = chunks
            st.session_state.index = index
            st.session_state.filename = uploaded.name
            st.session_state.history = []
            st.success(
                f"'{uploaded.name}' is ready — {len(chunks)} chunks indexed. Ask a question below."
            )
        finally:
            os.remove(tmp_path)

# ---- STEP 2: ask a question ----
if st.session_state.index is not None:
    question = st.text_input(
        "Your question", placeholder="e.g. which office had the highest collection?"
    )
    if st.button("Ask") and question.strip():
        with st.spinner("Thinking..."):
            top_chunks = retrieve(
                question, st.session_state.chunks, st.session_state.index, k=5
            )
            answer = answer_question(question, top_chunks)
            st.session_state.history.insert(0, (question, answer))

    # ---- show the conversation ----
    for q, a in st.session_state.history:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Answer:** {a}")
        st.divider()
else:
    st.info("Upload a document to begin.")
