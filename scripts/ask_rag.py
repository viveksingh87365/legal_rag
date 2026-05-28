import chromadb
import os

# IMPORTANT: safe persistent path
DB_PATH = os.path.join(os.getcwd(), "data/croma")

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    print("DEBUG RESULTS:", results)
    docs = results.get("documents")

    if not docs or len(docs[0]) == 0:
        return {
            "short_answer": "No answer found.",
            "reasoning": "No matching legal content found in database.",
            "key_points": ""
        }

    top_docs = docs[0]

    context = "\n\n".join(top_docs)

    return {
        "short_answer": top_docs[0][:500],
        "reasoning": context,
        "key_points": "Retrieved from legal Chroma DB"
    }