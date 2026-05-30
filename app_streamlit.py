import os
import zipfile
import streamlit as st
import gdown

# --- UPDATED DATABASE DOWNLOAD LOGIC (FOR STREAMLIT CLOUD) ---
DB_FOLDER = "data"

if not os.path.exists(DB_FOLDER):
    with st.spinner("Downloading legal database from Google Drive... Please wait."):
        try:
            file_id = "1NVwtteZY3_Q6Yoh0R0jqv1xufrQFaxPB"
            url = f"https://google.com{file_id}"
            gdown.download(url, "data.zip", quiet=False)
            
            with zipfile.ZipFile("data.zip", "r") as zip_ref:
                zip_ref.extractall(".")
                
            os.remove("data.zip")
        except Exception as e:
            st.error(f"Failed to download database: {e}")

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
