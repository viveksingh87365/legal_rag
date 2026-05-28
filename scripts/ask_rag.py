import os
import chromadb

os.makedirs("./data/croma", exist_ok=True)

client = chromadb.PersistentClient(path="./data/croma")

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
            "reasoning": "No data in database.",
            "key_points": ""
        }

    context = "\n\n".join(docs)

    return {
        "short_answer": context[:800],
        "reasoning": context,
        "key_points": "Generated from legal database"
    }