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
    
    answer_text = None
    errors_log = []
    
    try:
        api_key_val = str(st.secrets["GEMINI_API_KEY"]).strip()
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        # Define all candidate endpoints and their specific header layout variations
        configs = [
            # Pipeline 1: Native x-goog-api-key header (Recommended for AQ token formats)
            {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                "headers": {"Content-Type": "application/json", "x-goog-api-key": api_key_val},
                "params": {}
            },
            # Pipeline 2: Bearer Authorization Header (Standard for OAuth tokens)
            {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {api_key_val}"},
                "params": {}
            },
            # Pipeline 3: Standard parameter query routing fallback
            {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                "headers": {"Content-Type": "application/json"},
                "params": {"key": api_key_val}
            }
        ]
        
        # Loop through each network layout configuration automatically until one hits successfully
        for i, config in enumerate(configs, 1):
            try:
                res = requests.post(config["url"], headers=config["headers"], json=payload, params=config["params"])
                if res.status_code == 200:
                    res_json = res.json()
                    if "candidates" in res_json and res_json["candidates"]:
                        answer_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        break
                else:
                    errors_log.append(f"Pipeline {i} (Status {res.status_code}): {res.text[:100]}")
            except Exception as e:
                errors_log.append(f"Pipeline {i} Exception: {str(e)}")
                
        if not answer_text:
            answer_text = f"All API routing channels exhausted. Debug Details:\n" + "\n".join(errors_log)
            
    except Exception as master_error:
        answer_text = f"Master gateway execution error: {str(master_error)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Multi-channel adaptive router active"
    }
