import chromadb
import os

DB_PATH = os.path.abspath("data/croma")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):

    # DEBUG (IMPORTANT)
    print("DB PATH:", DB_PATH)
    print("COUNT:", collection.count())

    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    docs = results.get("documents", [[]])[0]

    if not docs:
        return {
            "short_answer": "No answer found.",
            "reasoning": "Chroma DB is empty in Streamlit environment.",
            "key_points": ""
        }

    return {
        "short_answer": docs[0][:800],
        "reasoning": "\n\n".join(docs),
        "key_points": "Retrieved from legal database"
    }