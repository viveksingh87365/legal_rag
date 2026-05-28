import chromadb
import os

DB_PATH = os.path.abspath("data/croma")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    docs = results.get("documents", [[]])[0]

    if not docs:
        return {
            "short_answer": "No answer found.",
            "reasoning": "DB not loaded in Streamlit Cloud.",
            "key_points": ""
        }

    return {
        "short_answer": docs[0][:800],
        "reasoning": "\n\n".join(docs),
        "key_points": "From legal DB"
    }