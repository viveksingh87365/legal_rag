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
        docs = raw_docs[0] if (raw_docs and len(raw_docs) > 0) else []
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
    
    context = "\n\n".join(docs)
    
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
        api_key_val = st.secrets["GEMINI_API_KEY"]
        
        # Bypassing the buggy SDK and calling the direct URL endpoint
        url = f"https://googleapis.com{api_key_val}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        
        # Parse the text answer safely from the direct API layout
        if "candidates" in response_json:
            answer_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in response_json:
            # Fallback configuration: If parameter auth complains, retry with standard Bearer token header
            fallback_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key_val}"
            }
            fallback_url = "https://googleapis.com"
            fallback_res = requests.post(fallback_url, headers=fallback_headers, json=payload)
            fallback_json = fallback_res.json()
            if "candidates" in fallback_json:
                answer_text = fallback_json["candidates"][0]["content"]["parts"][0]["text"]
            else:
                answer_text = f"API Error: {response_json['error']['message']}"
        else:
            answer_text = "Could not parse response from Gemini."
            
    except Exception as e:
        answer_text = f"Error generating point-wise answer: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Formatted via Direct API Endpoint Call"
    }
