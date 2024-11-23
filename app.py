import tempfile
import os
import sys
import streamlit as st  # type: ignore
import zipfile  # Added to handle ZIP files

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from log.logger import setup_logger
from processor import process_tender_document

logger = setup_logger("app_logs")

# Set the page configuration
st.set_page_config(
    page_title="Tender Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)




# Custom CSS for a modern look
st.markdown(
    """
    <style>
    /* Main page background */
    .main {
        background: linear-gradient(135deg, #f7f7f7, #e3f2fd);
        color: #333;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Title styling */
    .title {
        color: #2E86C1;
        font-size: 50px;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #e3f2fd, #ffffff);
        border-radius: 8px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }

    /* File uploader styling */
    .stFileUploader {
        border-radius: 8px;
        box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.1);
    }

    /* Processing info styling */
    .stInfo {
        background-color: #e8f4f8;
        border-left: 6px solid #007bff;
        color: #0b3954;
        padding: 15px;
        border-radius: 5px;
    }

    /* Relevance status and categories */
    .status {
        font-size: 30px;
        text-align: center;
        font-weight: bold;
        color: #007bff;
    }
    .categories {
        font-size: 25px;
        text-align: center;
        color: #28B463;
    }

    /* Keyword list */
    .keyword-list {
        font-size: 18px;
        margin-left: 20px;
        color: #333;
    }

    /* Separator line */
    hr {
        border: 1px solid #ddd;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #757575;
        margin-top: 50px;
    }
    .footer a {
        color: #007bff;
        text-decoration: none;
    }
    
    /* Styling for keyword occurrences */
    .keyword-item {
    background-color: #e1f5fe; /* Light blue background */
    border: 1px solid #bbdefb; /* Slightly darker border */
    border-radius: 5px; /* Rounded corners */
    padding: 10px; /* Padding for aesthetics */
    margin: 5px 0; /* Space between keywords */
    transition: transform 0.2s; /* Animation on hover */
    }
    
    .keyword-item:hover {
    transform: scale(1.02); /* Slight scale up on hover */
    }
    
    .badge {
    background-color: #28B463; /* Green background for relevance */
    color: white; /* White text */
    border-radius: 12px; /* Rounded corners */
    padding: 5px 10px; /* Padding for aesthetics */ 
    margin-left: 10px; /* Space from keyword */
    font-size: 14px; /* Font size */
    }      
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<div class="title">📄 Tender Document Analyzer</div>', unsafe_allow_html=True)

# # File uploader for PDF and ZIP files
# uploaded_file = st.file_uploader(
#     "Upload a PDF, DOCX or ZIP Document",
#     type=["pdf","docx", "zip"],  # Updated to accept 'zip' files
#     accept_multiple_files=False,
# )

# if uploaded_file is not None:
    
#     logger.info(f"Uploaded file: {uploaded_file.name}")
    
#     with tempfile.TemporaryDirectory() as tmp_dir:
#         file_path = os.path.join(tmp_dir, uploaded_file.name)

#         # Save the uploaded file to the temporary directory
#         try:
#             with open(file_path, "wb") as tmp_file:
#                 tmp_file.write(uploaded_file.read())
#         except Exception as e:
#             st.error(f"Error saving the uploaded file: {e}")
#             st.stop()

#         pdf_files = []

#         if uploaded_file.type == "application/zip" or uploaded_file.name.lower().endswith(".zip"):
            
#             logger.info("Processing ZIP file.")
            
#             # try:
#             #     with zipfile.ZipFile(file_path, 'r') as zip_ref:
#             #         zip_ref.extractall(tmp_dir)
#             # except zipfile.BadZipFile:
#             #     st.error("The uploaded ZIP file is corrupted or not a valid ZIP archive.")
#             #     st.stop()
#             # except Exception as e:
#             #     st.error(f"An error occurred while extracting the ZIP file: {e}")
#             #     st.stop()
                
                
#             try:
#                 with zipfile.ZipFile(file_path, 'r') as zip_ref:
#                     zip_ref.extractall(tmp_dir)
#                     extracted_files = zip_ref.namelist()
#                     if not extracted_files:
#                         st.error("The ZIP file is empty or could not be extracted.")
#                         logger.warning("ZIP extraction yielded no files.")
#                         st.stop()
#                 logger.info(f"Extracted ZIP to: {tmp_dir}")

#             except zipfile.BadZipFile:
#                 st.error("The uploaded ZIP file is corrupted or not a valid ZIP archive.")
#                 logger.warning("Bad ZIP file uploaded.")
#                 st.stop()
#             except Exception as e:
#                 st.error(f"An unexpected error occurred: {e}")
#                 logger.error(f"Unexpected error: {e}")
#                 st.stop()

#             # Walk through the extracted files to find all PDFs
#             for root, dirs, files in os.walk(tmp_dir):
#                 for file in files:
#                     if file.lower().endswith(".pdf") or file.lower().endswith(".docx"):
#                         file_path = os.path.join(root, file)
#                         pdf_files.append(file_path)  # Now includes DOCX files too
#                         logger.info(f"Document found: {file_path}")


#             if not pdf_files:
#                 st.error("No PDF files found in the uploaded ZIP archive.")
#                 logger.warning("No PDF files found in ZIP.")
#             else:
#                 logger.info(f"Total PDFs found: {len(pdf_files)}")
                        
#         elif uploaded_file.type == "application/pdf":
#             # If a single PDF is uploaded
#             pdf_files.append(file_path)
#         else:
#             st.error("Unsupported file type uploaded.")

#         if pdf_files:
#             # Display processing message
#             processing_placeholder = st.empty()
#             processing_placeholder.info(" Processing the document(s)... Please wait.")

#             # Process each PDF file
#             for idx, pdf in enumerate(pdf_files, 1):
#                 st.markdown(f"### Processing File {idx}: `{os.path.basename(pdf)}`")
                
#                 logger.info(f"Processing file {idx}: {pdf}")
                
#                 try:
#                     status, keyword_occurrences = process_tender_document(pdf)
#                 except Exception as e:
#                     st.error(f"An error occurred while processing {os.path.basename(pdf)}: {e}")
#                     continue  # Skip to the next file
                
#             # Process each document file (PDF or DOCX)
#             for idx, document in enumerate(pdf_files, 1):
#                 st.markdown(f"### Processing File {idx}: {os.path.basename(document)}")
                
#                 logger.info(f"Processing file {idx}: {document}")
                
#                 try:
#                     # extracted_text = extract_text_from_file(document)
#                     # Assume `process_tender_document` can handle extracted text from both PDF and DOCX
#                     status, keyword_occurrences = process_tender_document(document)
#                 except Exception as e:
#                     st.error(f"An error occurred while processing {os.path.basename(document)}: {e}")
#                     continue  # Skip to the next file

#                 # Display keyword occurrences
#                 if keyword_occurrences:
#                     st.markdown("#### **Keyword Occurrences:**")
#                     for occurrence in keyword_occurrences:
#                         st.text(occurrence)

                
#                 # if keyword_occurrences:
#                 #     st.markdown("#### **Keyword Occurrences:**")
#                 #     # Display each keyword occurrence with better formatting
#                 #     for idx, occurrence in enumerate(keyword_occurrences, 1):
#                 #         st.markdown(f"**{idx}. {occurrence}**")
#                 #         st.markdown("<hr>", unsafe_allow_html=True)  # Separator for readability
#                 # else:
#                 #     st.markdown("#### **No keywords found in this document.**")

#                 # Display relevancy statement in bold
                
#                 if status["Document Status"] == "Relevant":
#                     st.markdown(
#                         f'<div class="status"> {status["Document Status"]} | Categories: {status["Categories"]}</div>',
#                         unsafe_allow_html=True,
#                     )
#                 else:
#                     st.markdown(
#                         f'<div class="status"> {status["Document Status"]}</div>',
#                         unsafe_allow_html=True,
#                     )

#                 st.markdown("<hr>", unsafe_allow_html=True)  # Separator between documents

#             # Update the processing message to indicate completion
#             processing_placeholder.success("✅ Processing completed!")

# # Footer
# st.markdown(
#     """
#     <hr>
#     <div class="footer">
#         &copy; Tender Analyzer | Cimcon
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# ------------------------------------------------------------------------------------------------------

# File uploader for PDF and ZIP files
uploaded_file = st.file_uploader(
    "Upload a PDF, DOCX or ZIP Document",
    type=["pdf", "docx", "zip"],  # Updated to accept 'zip' files
    accept_multiple_files=False,
)

if uploaded_file is not None:
    
    logger.info(f"Uploaded file: {uploaded_file.name}")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, uploaded_file.name)

        # Save the uploaded file to the temporary directory
        try:
            with open(file_path, "wb") as tmp_file:
                tmp_file.write(uploaded_file.read())
        except Exception as e:
            st.error(f"Error saving the uploaded file: {e}")
            st.stop()

        pdf_files = []

        if uploaded_file.type == "application/zip" or uploaded_file.name.lower().endswith(".zip"):
            
            logger.info("Processing ZIP file.")
            
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                    extracted_files = zip_ref.namelist()
                    if not extracted_files:
                        st.error("The ZIP file is empty or could not be extracted.")
                        logger.warning("ZIP extraction yielded no files.")
                        st.stop()
                logger.info(f"Extracted ZIP to: {tmp_dir}")

            except zipfile.BadZipFile:
                st.error("The uploaded ZIP file is corrupted or not a valid ZIP archive.")
                logger.warning("Bad ZIP file uploaded.")
                st.stop()
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logger.error(f"Unexpected error: {e}")
                st.stop()

            # Walk through the extracted files to find all PDFs and DOCX
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    if file.lower().endswith(".pdf") or file.lower().endswith(".docx"):
                        file_path = os.path.join(root, file)
                        pdf_files.append(file_path)  # Now includes DOCX files too
                        logger.info(f"Document found: {file_path}")

            if not pdf_files:
                st.error("No PDF or DOCX files found in the uploaded ZIP archive.")
                logger.warning("No PDF or DOCX files found in ZIP.")
            else:
                logger.info(f"Total PDFs and DOCX files found: {len(pdf_files)}")
                        
        elif uploaded_file.type == "application/pdf" or uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # If a single PDF or DOCX is uploaded
            pdf_files.append(file_path)
        else:
            st.error("Unsupported file type uploaded.")

        if pdf_files:
            # Display processing message
            processing_placeholder = st.empty()
            processing_placeholder.info("Processing the document(s)... Please wait.")

            # Process each document file (PDF or DOCX)
            for idx, document in enumerate(pdf_files, 1):
                # Update the placeholder with the current processing file
                processing_placeholder.info(f"Processing File {idx} of {len(pdf_files)}: `{os.path.basename(document)}`")
                
                logger.info(f"Processing file {idx}: {document}")
                
                try:
                    status, keyword_occurrences = process_tender_document(document)
                except Exception as e:
                    st.error(f"An error occurred while processing {os.path.basename(document)}: {e}")
                    continue  # Skip to the next file

                # Display the document information and results
                st.markdown(f"### Processing File {idx}: `{os.path.basename(document)}`")

                if keyword_occurrences:
                    st.markdown("#### **Keyword Occurrences:**")
                    for occurrence in keyword_occurrences:
                        st.text(occurrence)

                # Display relevance status and categories
                if status["Document Status"] == "Relevant":
                    st.markdown(
                        f'<div class="status"> {status["Document Status"]} | Categories: {status["Categories"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="status"> {status["Document Status"]}</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("<hr>", unsafe_allow_html=True)  # Separator between documents

            # Update the processing message to indicate completion
            processing_placeholder.success("✅ Processing completed!")
