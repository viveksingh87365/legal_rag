import os
import chromadb
from pypdf import PdfReader
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Chroma database location
client = chromadb.PersistentClient(path="./data/croma")

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="legal_docs",
    embedding_function=embedding_function
)

pdf_folder = "./data/pdf"

doc_id = 0

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        path = os.path.join(pdf_folder, filename)

        print(f"Reading {filename}")

        reader = PdfReader(path)

        full_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        chunks = [
            full_text[i:i+1000]
            for i in range(0, len(full_text), 1000)
        ]

        for chunk in chunks:
            if chunk.strip():
                collection.add(
                    documents=[chunk],
                    ids=[f"doc_{doc_id}"]
                )
                doc_id += 1

print(f"Done. Added {doc_id} chunks.")
