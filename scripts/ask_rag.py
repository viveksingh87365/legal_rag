import os
import sys
import chromadb
import requests
import streamlit as st

def embed_text(text):
    api_key = st.secrets["GEMINI_API_KEY"]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"

    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [
                {"text": text}
            ]
        }
    }

    response = requests.post(url, json=payload)
    result = response.json()

    print("Embedding API result:", result)

    if "embedding" not in result:
        return None

    return result["embedding"]["values"]

def main(query):
   question_embedding = embed_text(question)

if question_embedding is None:
        return "Embedding failed. Check GEMINI_API_KEY in Streamlit Secrets."
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="legal_ai")
    
    # RAG pipeline logic
    question_embedding = embed_text(query)
    results = collection.query(query_embeddings=[question_embedding], n_results=3)
    
    context = ""
    if results and "documents" in results and results["documents"]:
        context = "\n".join(results["documents"][0])
        
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}\n\nAnswer the question based on the legal context provided."
    
    # Gemini Cloud API Request Block
    api_key = st.secrets["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    return answer
