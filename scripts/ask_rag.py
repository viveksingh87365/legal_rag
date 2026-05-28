import os
import chromadb

DB_PATH = os.path.join(os.getcwd(), "data", "croma")

os.makedirs(DB_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(name="legal_docs")

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