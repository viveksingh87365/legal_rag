import chromadb

client = chromadb.PersistentClient(path="./data/chroma")
collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results["documents"][0]

    if not docs:
        return {
            "short_answer": "No answer found.",
            "reasoning": "No matching legal content found in database.",
            "key_points": ""
        }

    context = "\n\n".join(docs)

    return {
        "short_answer": docs[0][:300],
        "reasoning": context,
        "key_points": "Answer generated from your legal PDF knowledge base."
    }