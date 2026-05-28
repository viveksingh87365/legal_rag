import chromadb

client = chromadb.PersistentClient(path="./data/croma")
collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results.get("documents", [])

    # SAFE CHECK (VERY IMPORTANT)
    if not docs or not docs[0]:
        return {
            "short_answer": "No answer found.",
            "reasoning": "No matching legal content found in database.",
            "key_points": ""
        }

    context_list = docs[0]

    context = "\n\n".join(context_list)

    return {
        "short_answer": context[:400],
        "reasoning": context,
        "key_points": "Answer generated from legal PDF database."
    }