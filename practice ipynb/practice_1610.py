import tempfile
import os
import sys
import streamlit as st # type: ignore
import zipfile

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))


from processor import process_tender_document


# Set the page configuration
st.set_page_config(
    page_title="Tender Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #F5F5F5;
    }
    .title {
        color: #2E86C1;
        font-size: 40px;
        text-align: center;
        padding: 20px;
    }
    .status {
        font-size: 30px;
        text-align: center;
        font-weight: bold;
    }
    .categories {
        font-size: 25px;
        text-align: center;
        color: #28B463;
    }
    .keyword-list {
        font-size: 18px;
        margin-left: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown('<div class="title">📄 Tender Document Analyzer</div>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload a PDF Document", type=["pdf"], accept_multiple_files=False)

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

      
    # Create placeholders for status messages
    processing_placeholder = st.empty()
    result_placeholder = st.empty()

    # Display processing message
    processing_placeholder.info("Processing the document... Please wait.")

    # Process the document
    status, keyword_occurrences = process_tender_document(tmp_file_path)

    # Remove the temporary file
    os.unlink(tmp_file_path)

    # Update the processing message to indicate completion
    processing_placeholder.success("Processing completed!")

    # Display keyword occurrences
    if keyword_occurrences:
        st.markdown("### **Keyword Occurrences:**")
        for occurrence in keyword_occurrences:
            st.text(occurrence)

    # Display relevancy statement in bold
    if status["Document Status"] == "Relevant":
        st.markdown(f'**Document Status: {status["Document Status"]} | Categories: {status["Categories"]}**', unsafe_allow_html=True)
    else:
        st.markdown(f'**Document Status: {status["Document Status"]}**', unsafe_allow_html=True)

# Footer
st.markdown("""
    <hr>
    <div style="text-align: center; color: gray;">
        &copy; 2024 Tender Analyzer App
    </div>
    """, unsafe_allow_html=True)
