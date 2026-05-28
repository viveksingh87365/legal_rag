from __future__ import annotations

import os
from pathlib import Path

import chromadb
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "chroma"

OLLAMA_URL = "http://localhost:11434"

EMBED_MODEL = "nomic-embed-text"

CHAT_MODEL = "mistral"


# Create embedding for question
def embed_text(text: str):

    response = requests.post(

        f"{OLLAMA_URL}/api/embed",

        json={
            "model": EMBED_MODEL,
            "input": text
        }
    )

    data = response.json()

    return data["embeddings"][0]


# Main program
def main(query):


    # Replace your hardcoded text string with this:
  question = query 


    # Connect database

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma")
client = chromadb.PersistentClient(path=db_path)


collection = client.get_or_create_collection(name="legal_ai")


    # Convert question into AI vector
question_embedding = embed_text(question)

    # Search similar legal text
results = collection.query(

        query_embeddings=[question_embedding],

        n_results=3
    )

documents = results["documents"][0]

    # Combine legal context
context = "\n\n".join(documents)

    # AI prompt
prompt = f"""
You are an Indian legal assistant for judges.

Answer shortly and accurately.

Use ONLY the provided legal context.

Question:
{question}

Legal Context:
{context}

Give:
1. Short legal answer
2. Relevant legal reasoning
3. Important legal point
"""

    # Ask AI
response = requests.post(

        f"{OLLAMA_URL}/api/chat",

        json={

            "model": CHAT_MODEL,

            "messages": [

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            "stream": False
        }
    )

data = response.json()

print("\n==========================================================")
print("AI LEGAL ANSWER by VIVEK KUMAR GEC AURANGABAD 2024-28(CSE)")
print("==========================================================\n")

print(data["message"]["content"])


# Run
if __name__ == "__main__":
    main()