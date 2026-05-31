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
        
        if raw_docs and isinstance(raw_docs, list) and len(raw_docs) > 0:
            docs = raw_docs
        else:
            docs = []
            
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
        
        # Route to the Vertex AI Express Mode endpoint using your specific project number
        url = "https://googleapis.com"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # Send the API request with the key as a safe parameter mapping
        response = requests.post(url, headers=headers, json=payload, params={"key": api_key_val})
        response_json = response.json()
        
        if "candidates" in response_json and response_json["candidates"]:
            first_candidate = response_json["candidates"][0]
            if "content" in first_candidate and "parts" in first_candidate["content"]:
                answer_text = first_candidate["content"]["parts"][0]["text"]
            else:
                answer_text = "Successfully connected, but could not parse text tokens from the response."
        elif "error" in response_json:
            answer_text = f"Vertex AI API Error: {response_json['error']['message']}"
        else:
            answer_text = f"Unrecognized API response layout: {str(response_json)[:200]}"
            
    except Exception as e:
        answer_text = f"API network exception error: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Routed via Enterprise Vertex AI Endpoint"
    }
