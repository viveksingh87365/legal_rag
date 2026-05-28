import os
import sys
import chromadb
import requests
import streamlit as st

def embed_text(text):
    import requests

API_KEY = "YOUR_NEW_KEY"

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [
        {
            "parts": [
                {"text": "Hello"}
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=data)

print(response.json())

def main(query):
    question = query
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="legal_ai")
    
    # RAG pipeline logic
    question_embedding = embed_text(question)
    results = collection.query(query_embeddings=[question_embedding], n_results=3)
    
    context = ""
    if results and "documents" in results and results["documents"]:
        context = "\n".join(results["documents"][0])
        
    prompt = f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer the question based on the legal context provided."
    
    # Gemini Cloud API Request Block
    api_key = st.secrets["GEMINI_API_KEY"]
    url = f"https://googleapis.com{api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    return answer
