import streamlit as st
import chromadb
from google import genai


def ask_rag(query):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        client = genai.Client(api_key=api_key)

        db = chromadb.PersistentClient(path="./data/chroma")
        collection = db.get_collection("legal_docs")

        results = collection.query(
            query_texts=[query],
            n_results=3
        )

        context = "\n\n".join(results["documents"][0])

        prompt = f"""
You are Kanun Saarthi GPT, an Indian legal assistant.

Answer the question using the legal context below.

Context:
{context}

Question:
{query}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"