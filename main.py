"""
main.py — run the RAG Document Q&A app.

Usage:
    python main.py --file data/sample_report.md
    python main.py --file data/sample_sales.csv

It loads the file, builds the RAG index once, then lets you ask questions in a loop.
Type 'quit' to exit.
"""

import argparse
from loader import load_file
from rag import chunk_text, build_index, retrieve, answer_question


def main():
    parser = argparse.ArgumentParser(description="RAG Document Q&A")
    parser.add_argument("--file", required=True, help="path to a pdf/txt/md/csv/xlsx file")
    parser.add_argument("--k", type=int, default=4, help="how many chunks to retrieve")
    args = parser.parse_args()

    # 1. LOAD the document text
    print(f"Loading {args.file} ...")
    text = load_file(args.file)

    # 2. CHUNK it
    chunks = chunk_text(text)
    print(f"Split into {len(chunks)} chunks.")

    # 3. EMBED + build the vector INDEX (one-time)
    print("Building the vector index (embedding chunks)...")
    index = build_index(chunks)
    print("Ready! Ask a question (type 'quit' to exit).\n")

    # 4 & 5. Loop: retrieve relevant chunks, then answer
    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit", "q", ""):
            print("Bye!")
            break
        top_chunks = retrieve(question, chunks, index, k=args.k)
        answer = answer_question(question, top_chunks)
        print(f"\nBot: {answer}\n")


if __name__ == "__main__":
    main()
