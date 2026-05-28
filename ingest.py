import os
def main():
    import chromadb
    # your ingestion logic here

if __name__ == "__main__":
    main()


# Chroma database location

DB_PATH = os.path.join(os.getcwd(), "data", "croma")
os.makedirs(DB_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=DB_PATH)

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
