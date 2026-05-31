import os
import zipfile
import streamlit as st
import gdown

# --- UPDATED DATABASE DOWNLOAD LOGIC (FOR STREAMLIT CLOUD) ---
DB_FOLDER = "data"
# --- ENHANCED DATABASE VERIFICATION ---
DB_FOLDER = os.path.join("data", "croma")
# Check if the folder doesn't exist OR if it is completely empty
is_db_empty = not os.path.exists(DB_FOLDER) or len(os.listdir(DB_FOLDER)) == 0

if is_db_empty:
    st.info("Database empty or missing. Starting 403MB download from Google Drive...")
    file_id = "1NWwtteZY3_Q6Yoh0RQjqv1xufrQFaxPB"
    
    try:
        url = f"https://google.com{file_id}"
        gdown.download(url, output="data.zip", quiet=False, fuzzy=True)
        
        if os.path.exists("data.zip"):
            import zipfile
            with zipfile.ZipFile("data.zip", "r") as zip_ref:
                zip_ref.extractall(".")
            os.remove("data.zip")
            st.success("Database fully downloaded and extracted!")
    except Exception as download_error:
        st.error(f"Download failed: {download_error}")
else:
    st.sidebar.success("Database loaded successfully from local cache!")


           
    except Exception as download_error:
        st.error(f"Download failed: {download_error}. Please try rebooting the app.")
else:
    st.sidebar.success("Database loaded from local cache!")

    
    if os.path.exists("data.zip"):
        os.remove("data.zip")
    st.success("Database ready!")



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
