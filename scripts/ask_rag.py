import chromadb
import os

DB_PATH = os.path.abspath("./data/croma")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):

    print("DB PATH:", DB_PATH)
    print("COLLECTION COUNT:", collection.count())

    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    print("DEBUG RESULTS:", results)

    docs = results.get("documents", [[]])[0]

    if len(docs) == 0:
        return {
            "short_answer": "No answer found.",
            "reasoning": "EMPTY RESULTS FROM CHROMA",
            "key_points": ""
        }

    return {
        "short_answer": docs[0][:800],
        "reasoning": "\n\n".join(docs),
        "key_points": "From DB"
    }