import os

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

import re

import io

import sys
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
        with st.spinner("Processing your legal query against document vector store..."):
            response = run_rag_and_parse(user_question)
            
        if "error" in response:
            st.error(response["error"])
        else:
            st.success("Analysis Complete!")
            st.markdown("---")
            
            # Subheader 1
            st.subheader("1. Short Legal Answer")
            st.info(response["short_answer"])
            
            # Subheader 2
            st.subheader("2. Relevant Legal Reasoning")
            st.write(response["legal_reasoning"])
            
            # Subheader 3
            st.subheader("3. Important Legal Point")
            st.warning(response["important_point"])
            
            # Hidden debug expander to view raw unparsed logs if needed
            with st.expander("View Raw Console Output Log"):
                st.code(response["raw_fallback"])
