import streamlit as st
import chromadb
from google import genai


def ask_rag(question):
    try:
        # Load API key from Streamlit secrets
        api_key = st.secrets["GEMINI_API_KEY"]

        # Gemini client
        client = genai.Client(api_key=api_key)

        # Connect Chroma database
        db = chromadb.PersistentClient(path="./data/chroma")
        collection = db.get_collection("legal_docs")

        # Search relevant chunks
        results = collection.query(
            query_texts=[question],
            n_results=3
        )

        context = "\n\n".join(results["documents"][0])

        prompt = f"""
You are an Indian legal assistant.

Answer the question clearly using the legal context below.

Context:
{context}

Question:
{question}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"