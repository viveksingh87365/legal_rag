import os
import chromadb
from google import genai

# Automatically try both "croma" and "chroma" to find where the data is stored
if os.path.exists(os.path.join(os.getcwd(), "data", "croma")):
    DB_PATH = os.path.join(os.getcwd(), "data", "croma")
elif os.path.exists(os.path.join(os.getcwd(), "data", "chroma")):
    DB_PATH = os.path.join(os.getcwd(), "data", "chroma")
else:
    DB_PATH = os.path.join(os.getcwd(), "data")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="legal_docs")

def ask_rag(query):
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    
    # Get the raw list of documents
    raw_docs = results.get("documents", [])
    
    # Extract the first inner list safely
    docs = raw_docs[0] if raw_docs else []
    
    if not docs or len(docs) == 0:
        return {
            "short_answer": "No answer found.",
            "reasoning": f"Database folder located at {DB_PATH} but no matching documents were retrieved.",
            "key_points": ""
        }
    
    # Combine the database document text into a single context block
    context = "\n\n".join(docs)
    
    # Set up the Gemini client
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
