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
        raw_docs = results.get("documents", [[]])
        docs = raw_docs if raw_docs else []
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
    
    # Configure the stable client using your exact secret key string
    try:
        api_key_val = st.secrets["GEMINI_API_KEY"]
        tg_genai.configure(api_key=api_key_val)
        # Using the standard flash model compatible with the stable library
        model = tg_genai.GenerativeModel('gemini-1.5-flash')
    except Exception as secret_error:
        return {
            "short_answer": "Secrets Configuration Error",
            "reasoning": f"Could not initialize Gemini: {str(secret_error)}",
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
        answer_text = f"Error generating point-wise answer: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Formatted via Stable Gemini API"
    }
