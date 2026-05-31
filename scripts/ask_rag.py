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
        
        # Safely unpack nested list structure
        if raw_docs and isinstance(raw_docs, list) and len(raw_docs) > 0:
            docs = raw_docs[0]
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
    
    # Clean lists or strings safely
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
        url = "https://googleapis.com"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # Attempt 1: Passing key via parameters
        response = requests.post(url, headers=headers, json=payload, params={"key": api_key_val})
        
        try:
            response_json = response.json()
            if "candidates" in response_json and response_json["candidates"]:
                answer_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            elif "error" in response_json:
                answer_text = f"API Error: {response_json['error']['message']}"
            else:
                answer_text = f"Unrecognized JSON structure: {str(response_json)}"
        except Exception:
            # Attempt 2: Fallback to standard Header Authorization for enterprise token formats
            headers["Authorization"] = f"Bearer {api_key_val}"
            fallback_res = requests.post(url, headers=headers, json=payload)
            try:
                fallback_json = fallback_res.json()
                if "candidates" in fallback_json and fallback_json["candidates"]:
                    answer_text = fallback_json["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    answer_text = f"Token authorized but failed. Server details: {fallback_res.text[:200]}"
            except Exception:
                answer_text = f"Authentication error. Server response: {response.text[:150]}"
            
    except Exception as e:
        answer_text = f"Generation error exception: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Direct safe HTTP channel validation"
    }
