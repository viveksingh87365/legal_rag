import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import re
import io
import sys
from contextlib import redirect_stdout

# Import your script's main logic
# Assumes scripts/ask_rag.py has a function or can be invoked
try:
    import scripts.ask_rag as ask_rag
except ImportError:
    st.error("Could not import 'scripts.ask_rag'. Ensure you run Streamlit from the root directory containing the 'scripts' folder.")

def run_rag_and_parse(question: str):
    """
    Executes the RAG pipeline logic and extracts structured blocks 
    using regex based on your terminal print layout.
    """
    # 1. Capture stdout in case your script relies on print() statements
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            # OPTION A: If your script has a function that accepts a string question
            if hasattr(ask_rag, 'get_legal_answer'):
                output_text = ask_rag.get_legal_answer(question)
            elif hasattr(ask_rag, 'main'):
                # If your main function takes arguments or uses sys.argv
                output_text = ask_rag.main(question)
            else:
                # OPTION B: If running the file directly executes it via standard input simulation
                # We temporarily mock sys.argv or handle it via a fallback
                output_text = "" 
        except Exception as e:
            return {"error": f"Error running RAG pipeline: {str(e)}"}

    # If the function returned nothing but printed to terminal, read the printed text
    console_output = f.getvalue()
    full_text = output_text if output_text else console_output

    # 2. Parse the text blocks using Regular Expressions based on your console format
    short_answer_match = re.search(r'1\.\s*Short\s*Legal\s*Answer:\s*(.*?)(?=\n\s*2\.)', full_text, re.DOTALL | re.IGNORECASE)
    reasoning_match = re.search(r'2\.\s*Relevant\s*Legal\s*Reasoning:\s*(.*?)(?=\n\s*3\.)', full_text, re.DOTALL | re.IGNORECASE)
    # Captures everything after point 3 up to the next command prompt or line break boundary
    point_match = re.search(r'3\.\s*Important\s*Legal\s*Point:\s*(.*?)(?=\n\s*\(|$)', full_text, re.DOTALL | re.IGNORECASE)

    # 3. Clean up the parsed outputs or fallback if regex fails
    return {
        "short_answer": short_answer_match.group(1).strip() if short_answer_match else "No explicit short answer returned.",
        "legal_reasoning": reasoning_match.group(1).strip() if reasoning_match else "No explicit reasoning returned.",
        "important_point": point_match.group(1).strip() if point_match else "No explicit key points returned.",
        "raw_fallback": full_text # Back up in case format changes
    }

# ----------------- STREAMLIT UI LAYOUT -----------------

st.set_page_config(page_title="AI Legal Assistant", page_icon="⚖️", layout="centered")

st.title("⚖️ AI Legal Assistant")
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
