import os
import chromadb
from google import genai

DB_PATH = os.path.join(os.getcwd(), "data", "croma")
os.makedirs(DB_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="legal_docs")

def ask_rag(query):
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    
    docs = results.get("documents", [[]])[0]
    
    if not docs:
        return {
            "short_answer": "No answer found.",
            "reasoning": "DB not loaded in Streamlit Cloud.",
            "key_points": ""
        }
    
    # Combine the database document text into a single context block
    context = "\n\n".join(docs)
    
    # Set up the Gemini client (it will automatically look for your secret API key)
    ai_client = genai.Client()
    
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
