import chromadb

# connect to Chroma database
client = chromadb.PersistentClient(path="./data/chroma")

# load collection
collection = client.get_or_create_collection("legal_docs")


def ask_rag(query):
    # search relevant docs
    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    context = "\n".join(results["documents"][0])

    # temporary answer
    answer = f"""
1. Short Legal Answer
IPC means Indian Penal Code.

2. Relevant Legal Reasoning
The Indian Penal Code (IPC) is the main criminal law code of India. It defines crimes and punishments.

3. Important Legal Point
IPC came into force in 1860.
Example:
Section 302 → Murder
Section 420 → Cheating

Relevant context:
{context}
"""

    return answer