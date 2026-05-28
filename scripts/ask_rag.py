import os
import chromadb

DB_PATH = os.path.join(os.getcwd(), "data/croma")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    print("DEBUG:", results)

    docs = results.get("documents", [[]])[0]

    if not docs:
        return {
            "short_answer": "No answer found.",
            "reasoning": "DB empty or not loaded in Streamlit Cloud.",
            "key_points": ""
        }

    context = "\n\n".join(docs)

    return {
        "short_answer": docs[0][:800],
        "reasoning": context,
        "key_points": "From legal DB"
    }