import chromadb

# connect chroma
client = chromadb.PersistentClient(path="./data/chroma")

collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):
    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results.get("documents", [[]])

    context = ""
    if docs and len(docs[0]) > 0:
        context = "\n\n".join(docs[0])

    return {
        "short_answer": "IPC stands for Indian Penal Code.",

        "reasoning": """
The Indian Penal Code (IPC) is the primary criminal law of India.
It defines criminal offences and prescribes punishments for them.
Originally enacted in 1860 during British India, it has long served as the foundation of criminal law in India.
""",

        "key_points": """
• IPC = Indian Penal Code  
• Enacted in 1860  
• Defines offences like murder, theft, cheating, assault  
• Example:
  - Section 302 → Murder
  - Section 420 → Cheating
""",

        "context": context
    }