import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./data/croma")

collection = client.get_collection(
    name="legal_docs",
    embedding_function=embedding_function
)


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
        "short_answer": context[:700],
        "reasoning": context,
        "key_points": "Generated from legal database"
    }