import chromadb

client = chromadb.PersistentClient(path="./data/croma")
collection = client.get_collection("legal_docs")


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    docs = results.get("documents", [[]])[0]

    if not docs:
        return {
            "short_answer": "No answer found.",
            "reasoning": "No matching legal content found in database.",
            "key_points": ""
        }

    context = "\n\n".join(docs)

    return {
        "short_answer": context[:800],
        "reasoning": context,
        "key_points": "Generated from legal database"
    }