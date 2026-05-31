import os
import chromadb
import google.generativeai as tg_genai
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
        
        # Safely extract the inner list of strings from ChromaDB's nested format
        raw_docs = results.get("documents", [])
        if raw_docs and len(raw_docs) > 0:
            docs = raw_docs[0]  # Unpacks the list of document contents safely
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
    
    # Clean and combine document texts securely without sequence/type errors
    context = "\n\n".join([str(d) for d in docs])
    
    # Configure the client using your secret AQ. key string
    try:
        api_key_val = str(st.secrets["GEMINI_API_KEY"]).strip()
        tg_genai.configure(api_key=api_key_val)
        model = tg_genai.GenerativeModel('gemini-1.5-flash')
    except Exception as secret_error:
        return {
            "short_answer": "Secrets Configuration Error",
            "reasoning": f"Could not initialize Gemini SDK: {str(secret_error)}",
            "key_points": ""
        }
    
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
        response = model.generate_content(prompt)
        answer_text = response.text
    except Exception as e:
        answer_text = f"Error generating point-wise answer from SDK: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Successfully authenticated via stable Gemini SDK pipeline"
    }
