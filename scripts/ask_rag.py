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
    
    # Safely clean and combine the document strings
    clean_docs = [str(d) for d in docs if isinstance(d, str)]
    if not clean_docs and docs and isinstance(docs, list) and isinstance(docs[0], list):
        clean_docs = [str(d) for d in docs[0] if isinstance(d, str)]
        
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
        # Get the secret API key and strip out any accidental whitespace characters
        api_key_val = str(st.secrets["GEMINI_API_KEY"]).strip()
        
        # Clean, static web link format
        url = "https://googleapis.com"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # Passing the key inside params prevents website address corruption bugs
        response = requests.post(url, headers=headers, json=payload, params={"key": api_key_val})
        response_json = response.json()
        
        # Safely parse out the text response
        if "candidates" in response_json and response_json["candidates"]:
            candidate = response_json["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                answer_text = candidate["content"]["parts"][0]["text"]
            else:
                answer_text = "Could not parse response text format from Gemini."
        elif "error" in response_json:
            answer_text = f"API Error: {response_json['error']['message']}"
        else:
            answer_text = "Empty or unrecognized response schema from Gemini API."
            
    except Exception as e:
        answer_text = f"Error generating point-wise answer: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Formatted via Direct Safe Parameter API Call"
    }
