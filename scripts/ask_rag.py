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
        raw_docs = results.get("documents", [])
        if raw_docs and len(raw_docs) > 0:
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
    
    # Safely convert all retrieved database items to clear strings
    clean_docs = [str(d) for d in docs]
    context = "\n\n".join(clean_docs)
    
    prompt = f"""You are an expert legal assistant. Use the following context to answer the user's question accurately.

Context:
{context}

Question: {query}

CRITICAL STRUCTURAL RULES:
1. Do not use long paragraphs.
2. Provide a 1-sentence clear direct summary first.
3. Break down the key reasoning into short, accurate, point-wise bullets."""
    
    try:
        # Extract secret token string cleanly and strip spaces
        api_key_val = str(st.secrets["GEMINI_API_KEY"]).strip()
        
        # Static URL without using f-string parameter insertion to guarantee zero string formatting errors
        url = "https://googleapis.com"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # Passing the tracking key safely inside the query parameters dictionary
        response = requests.post(url, headers=headers, json=payload, params={"key": api_key_val})
        
        if response.status_code == 200:
            response_json = response.json()
            if "candidates" in response_json and response_json["candidates"]:
                answer_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            else:
                answer_text = "API linked successfully, but text answer object is missing structure."
        else:
            answer_text = f"Authentication Error ({response.status_code}): {response.text[:200]}"
            
    except Exception as e:
        answer_text = f"API background network communication failure: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Authenticated via Stable URL Parameter Mapping"
    }
