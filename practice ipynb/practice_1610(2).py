import tempfile
import os
import sys
import streamlit as st  # type: ignore
import zipfile  # Added to handle ZIP files

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from processor import process_tender_document

# Set the page configuration
st.set_page_config(
    page_title="Tender Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<div class="title">📄 Tender Document Analyzer</div>', unsafe_allow_html=True)

# File uploader now accepts both PDF and ZIP files
uploaded_file = st.file_uploader(
    "Upload a PDF or ZIP Document",
    type=["pdf", "zip"],  # Updated to accept 'zip' files
    accept_multiple_files=False,
)

if uploaded_file is not None:
    # Create a temporary directory to handle uploads and extractions
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, uploaded_file.name)

        # Save the uploaded file to the temporary directory
        with open(file_path, "wb") as tmp_file:
            tmp_file.write(uploaded_file.read())

        pdf_files = []

        if uploaded_file.type == "application/zip":
            # Handle ZIP file extraction
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)

            # Walk through the extracted files to find all PDFs
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_path = os.path.join(root, file)
                        pdf_files.append(pdf_path)

            if not pdf_files:
                st.error("No PDF files found in the uploaded ZIP archive.")
        elif uploaded_file.type == "application/pdf":
            # If a single PDF is uploaded
            pdf_files.append(file_path)
        else:
            st.error("Unsupported file type uploaded.")

        if pdf_files:
            # Display processing message
            processing_placeholder = st.empty()
            processing_placeholder.info("Processing the document(s)... Please wait.")

            # Process each PDF file
            for idx, pdf in enumerate(pdf_files, 1):
                st.markdown(f"### Processing File {idx}: `{os.path.basename(pdf)}`")
                status, keyword_occurrences = process_tender_document(pdf)

                # Display keyword occurrences
                if keyword_occurrences:
                    st.markdown("#### **Keyword Occurrences:**")
                    for occurrence in keyword_occurrences:
                        st.text(occurrence)
                else:
                    st.markdown("#### **No keywords found in this document.**")

                # Display relevancy statement in bold
                if status["Document Status"] == "Relevant":
                    st.markdown(
                        f'**Document Status: {status["Document Status"]} | Categories: {status["Categories"]}**',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'**Document Status: {status["Document Status"]}**',
                        unsafe_allow_html=True,
                    )

                st.markdown("---")  # Separator between documents

            # Update the processing message to indicate completion
            processing_placeholder.success("Processing completed!")

# Footer
st.markdown(
    """
    <hr>
    <div style="text-align: center; color: gray;">
        &copy; 2024 Tender Analyzer App
    </div>
    """,
    unsafe_allow_html=True,
)
