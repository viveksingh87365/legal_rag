import chromadb

client = chromadb.PersistentClient(path="./data/croma")
collection = client.get_collection("legal_docs")


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results["documents"]

    # IMPORTANT FIX
    if not docs or not docs[0]:
        return {
            "short_answer": "No answer found.",
            "reasoning": "No matching legal content found.",
            "key_points": ""
        }

    flat_docs = docs[0]

    context = "\n\n".join(flat_docs)

    return {
        "short_answer": flat_docs[0][:500],
        "reasoning": context,
        "key_points": "Retrieved from IPC legal database"
    }