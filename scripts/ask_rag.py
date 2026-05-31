import os
import chromadb
import requests
import streamlit as st

DB_PATH = os.path.join(os.getcwd(), "data", "croma")

def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name="legal_docs")

def ask_rag(query):
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=5
        )
        raw_docs = results.get("documents", [[]])
        docs = raw_docs if (raw_docs and len(raw_docs) > 0) else []
    except Exception as db_error:
        return {
            "short_answer": "Database connection error.",
            "reasoning": f"ChromaDB error: {str(db_error)}",
            "key_points": ""
        }
    
    if not docs:
        return {
            "short_answer": "No matching documents found.",
            "reasoning": "The database is connected but contains 0 documents.",
            "key_points": ""
        }
    
    clean_docs = []
    for item in docs:
        if isinstance(item, list):
            clean_docs.extend([str(x) for x in item])
        else:
            clean_docs.append(str(item))
            
    context = "\n\n".join(clean_docs)
    
    prompt = f"""
    You are an expert legal assistant. Use the following context to answer the user's question accurately.
    
    Context:
    {context}
    
    Question: {query}
    
    CRITICAL STRUCTURAL RULES:
    1. Do not use long paragraphs.
    2. Provide a 1-sentence clear direct summary first.
    3. Break down the key reasoning into short, accurate, point-wise bullets.
    """
    
    try:
        api_key_val = str(st.secrets["GEMINI_API_KEY"]).strip()
        
        # Using Google's OpenAI-compatible endpoint which accepts corporate access tokens
        url = "https://generativelanguage.googleapis.com/v1beta/chat/completions"
        
        # Passing the AQ. token inside a standard Authorization Bearer header
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key_val}"
        }
        
        # Reformatting the payload schema to match OpenAI standards required by this endpoint
        payload = {
            "model": "gemini-1.5-flash",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            response_json = response.json()
            if "choices" in response_json and len(response_json["choices"]) > 0:
                answer_text = response_json["choices"][0]["message"]["content"]
            else:
                answer_text = f"API success, but unexpected OpenAI schema format returned: {str(response_json)[:150]}"
        else:
            answer_text = f"Authentication Error ({response.status_code}): {response.text[:200]}"
            
    except Exception as e:
        answer_text = f"API background network communication failure: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Authenticated via OpenAI Compatibility Layer"
    }
