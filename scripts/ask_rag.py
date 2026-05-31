import os
import chromadb
from google import genai

DB_PATH = os.path.join(os.getcwd(), "data", "croma")

def get_collection():
    # Only initialize the client when a query is actually made
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name="legal_docs")

def ask_rag(query):
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=5
        )
        
        # Safely get the list of document strings
        raw_docs = results.get("documents", [[]])
        docs = raw_docs[0] if raw_docs else []
        
    except Exception as db_error:
        return {
            "short_answer": "Database connection error.",
            "reasoning": f"ChromaDB error: {str(db_error)}",
            "key_points": ""
        }
    
    if not docs:
        return {
            "short_answer": "No matching documents found.",
            "reasoning": "The database is connected but contains 0 documents. It needs to be re-downloaded.",
            "key_points": ""
        }
    
    context = "\n\n".join(docs)
    # Set up the Gemini client with explicit Streamlit secrets authentication
    import streamlit as st
    ai_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    
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
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        answer_text = response.text
    except Exception as e:
        answer_text = f"Error generating point-wise answer: {str(e)}"

    return {
        "short_answer": answer_text,
        "reasoning": context,
        "key_points": "Formatted via Gemini AI Studio"
    }
