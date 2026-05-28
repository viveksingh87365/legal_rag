import chromadb
import subprocess
import os

DB_PATH = "/tmp/chroma_db"

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("legal_docs")


# auto rebuild if empty
if collection.count() == 0:
    subprocess.run(["python3", "ingest.py"])


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    docs = results.get("documents", [[]])[0]

    if not docs:
        return {
            "short_answer": "No answer found.",
            "reasoning": "Database not loaded in cloud.",
            "key_points": ""
        }

    context = "\n\n".join(docs)

    return {
        "short_answer": docs[0][:800],
        "reasoning": context,
        "key_points": "From legal DB"
    }