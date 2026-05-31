# --- ADVANCED LARGE FILE DOWNLOAD WITH COOKIE HANDLING ---
import os
import zipfile
import requests
import streamlit as st

DB_FOLDER = os.path.join("data", "croma")

if not os.path.exists(DB_FOLDER) or not os.listdir(DB_FOLDER):
    st.info("Database files missing. Downloading 403MB archive from Google Drive...")
    destination = "data.zip"
    file_id = "1NVwtteZY3_Q6Yoh0RQjqv1xufrQFaxPB"
    
    try:
        session = requests.Session()
        URL = "https://google.com"
        
        # Step 1: Send a request to look for Google's large file warning cookie
        response = session.get(URL, params={'id': file_id}, stream=True)
        
        token = None
        for key, value in response.cookies.items():
            if 'download_warning' in key:
                token = value
                break
                
        # Step 2: If the warning token exists, pass it back to confirm the download
        if token:
            response = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)
            
        # Step 3: Save the streaming data locally
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
                    
        # Step 4: Verify if it's a real zip file before attempting extraction
        if zipfile.is_zipfile(destination):
            with zipfile.ZipFile(destination, "r") as zip_ref:
                zip_ref.extractall(".")
            os.remove(destination)
            st.success("Database successfully downloaded and extracted!")
        else:
            # Read the first few lines of the file to see the actual error message from Google
            with open(destination, "r", errors="ignore") as f:
                google_error = f.read(300)
            st.error(f"Download failed. Google Drive blocked the file stream. Reason: {google_error[:150]}")
            if os.path.exists(destination):
                os.remove(destination)
            
    except Exception as download_error:
        st.error(f"Download failed: {download_error}")
else:
    st.sidebar.success("Database loaded successfully from local cache!")


# ---------------------------------------------------------

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
import io
from contextlib import redirect_stdout
import scripts.ask_rag as ask_rag

def run_rag_and_parse(question: str):
    try:
        result = ask_rag.ask_rag(question)

        if isinstance(result, dict):
            return {
                "short_answer": result.get("short_answer", "No short answer available."),
                "legal_reasoning": result.get("reasoning", "No reasoning available."),
                "important_point": result.get("key_points", "No important point available."),
                "raw_fallback": str(result)
            }

        return {
            "short_answer": str(result),
            "legal_reasoning": "",
            "important_point": "",
            "raw_fallback": str(result)
        }

    except Exception as e:
        return {
            "error": str(e)
        }

# ----------------- STREAMLIT UI LAYOUT -----------------

st.set_page_config(page_title="AI Legal Assistant", page_icon="⚖️", layout="centered")

st.title("⚖️ KAKUNSARHIGPT - Your AI Legal Assistant")
st.caption("AI LEGAL ANSWER by VIVEK KUMAR GEC AURANGABAD 2024-28 (CSE)")
st.markdown("---")

user_question = st.text_area(
    "Ask your legal question:", 
    placeholder="e.g., if dm denied to hear my problem then what action can i do",
    height=100
)

if st.button("Get Legal Advice", type="primary"):
    if not user_question.strip():
        st.warning("Please type a valid question first.")
    else:
        response = run_rag_and_parse(user_question)

        if "error" in response:
            st.error(response["error"])
        else:
            st.success("Analysis Complete!")

            st.subheader("1. Short Legal Answer")
            st.info(response.get("short_answer", ""))

            st.subheader("2. Relevant Legal Reasoning")
            st.write(response.get("legal_reasoning", ""))

            st.subheader("3. Important Legal Point")
            st.warning(response.get("important_point", ""))
# Cache Reset: Sat May 30 16:05:29 IST 2026
