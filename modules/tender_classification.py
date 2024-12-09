import os
import sys
import rarfile
import streamlit as st  # type: ignore
import zipfile  # Added to handle ZIP files
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv # type: ignore


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from log.logger import setup_logger
from core.processor import process_tender_document



# Load environment variables0
load_dotenv()   
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


    
processing_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, max_output_tokens=8192)



logger = setup_logger("tender_classification_logs")



def process_with_llm(status, keyword_occurrences,llm_model):
    
    document_status = status.get("Document Status")
    categories = status.get("Categories")

    
    processing_prompt = (
    "You are analyzing a document based on its status of relevancy and its associated categories. Your task is to ensure all information "
    "is preserved and presented in a structured manner without losing any details. Please follow the guidelines below:\n\n"
    "1. Document Relevance Status: Clearly state if the document is relevant or not based on the provided status.\n"
    "   - Also, mention the associated categories.\n"
    "2. Keywords Analysis:\n"
    "   - If the status indicates relevance, display all keywords along with their reference page numbers.\n"
    "   - Present the keywords and page numbers in a **table format**.\n"
    "   - If the status is not relevant, do not provide keywords, and only mention the irrelevance.\n\n"
    "Here is the information to analyze:\n\n"
    f"**Status of the Document**:\n\n**{document_status}**\n\n"
    f"**Categories**:\n\n**{categories}**\n\n"
    f"Keywords and Reference Pages: {keyword_occurrences}\n\n"
    "Note: Alway provide this Status of the Document, Category in Bold format in order to highlight that."
    "Provide a structured response that adheres to the above guidelines, and ensure the keywords and reference page numbers are in a table format."
    )

    
    try:
        # Use the LLM to process the data
        response = llm_model.invoke(processing_prompt)
        
        # return response.content
        return response.content
    
    except Exception as e:
        logger.error(f"Error during LLM processing: {e}")
        return "Error: Unable to process with LLM."
    





# def process_uploaded_file(uploaded_file, upload_directory):

#     logger.info(f"Uploaded file: {uploaded_file.name}")

#     # Define the permanent file path
#     file_path = os.path.join(upload_directory, uploaded_file.name)

#     # Save the uploaded file to the permanent directory
#     try:
#         with open(file_path, "wb") as perm_file:
#             perm_file.write(uploaded_file.read())
#     except Exception as e:
#         st.error(f"Error saving the uploaded file: {e}")
#         st.stop()

#     # List to track files for the current session
#     current_session_files = []

#     # Handle ZIP files
#     if uploaded_file.type == "application/zip" or uploaded_file.name.lower().endswith(".zip"):
#         logger.info("Processing ZIP file.")
#         try:
#             with zipfile.ZipFile(file_path, 'r') as zip_ref:
#                 zip_ref.extractall(upload_directory)  # Extract directly to permanent directory
#                 extracted_files = zip_ref.namelist()
#                 if not extracted_files:
#                     st.error("The ZIP file is empty or could not be extracted.")
#                     logger.warning("ZIP extraction yielded no files.")
#                     st.stop()
#                 # Add extracted files to current session list
#                 current_session_files.extend(
#                     [os.path.join(upload_directory, file) for file in extracted_files]
#                 )
#             logger.info(f"Extracted ZIP to: {upload_directory}")
#         except zipfile.BadZipFile:
#             st.error("The uploaded ZIP file is corrupted or not a valid ZIP archive.")
#             logger.warning("Bad ZIP file uploaded.")
#             st.stop()
#         except Exception as e:
#             st.error(f"An unexpected error occurred: {e}")
#             logger.error(f"Unexpected error: {e}")
#             st.stop()

#     # Handle single PDF or DOCX files
#     elif uploaded_file.type == "application/pdf" or uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#         current_session_files.append(file_path)
#     else:
#         st.error("Unsupported file type uploaded.")
#         return

#     # Filter and process only the current session files
#     if current_session_files:
#         # Display processing message
#         processing_placeholder = st.empty()
#         processing_placeholder.info("Processing the document(s)... Please wait.")

#         # Process each document file (PDF or DOCX)
#         for idx, document in enumerate(current_session_files, 1):
#             # Update the placeholder with the current processing file
#             processing_placeholder.info(f"Processing File {idx} of {len(current_session_files)}: `{os.path.basename(document)}`")

#             logger.info(f"Processing file {idx}: {document}")

#             try:
#                 # Process the document to extract status and keyword occurrences
#                 status, keyword_occurrences = process_tender_document(document)

#                 # LLM Processing Step
#                 llm_response = process_with_llm(status, keyword_occurrences, processing_model)

#             except Exception as e:
#                 st.error(f"An error occurred while processing {os.path.basename(document)}: {e}")
#                 continue  # Skip to the next file

#             # Display the document information and results
#             st.markdown(f"### Processing File {idx}: `{os.path.basename(document)}`")
#             st.markdown("#### Keywords and Reference Pages:")
#             st.markdown(llm_response)
#             st.markdown("<hr>", unsafe_allow_html=True)  # Separator between documents

#         # Update the processing message to indicate completion
#         processing_placeholder.success("✅ Processing completed!")


def process_uploaded_file(uploaded_file, upload_directory):

    logger.info(f"Uploaded file: {uploaded_file.name}")

    # Handle ZIP files
    if uploaded_file.type == "application/zip" or uploaded_file.name.lower().endswith(".zip"):
        logger.info("Processing ZIP file.")
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(upload_directory)  # Extract directly to permanent directory
                logger.info(f"Extracted ZIP to: {upload_directory}")
        except zipfile.BadZipFile:
            st.error("The uploaded ZIP file is corrupted or not a valid ZIP archive.")
            logger.warning("Bad ZIP file uploaded.")
            st.stop()
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error: {e}")
            st.stop()

    # Handle RAR files
    elif uploaded_file.name.lower().endswith(".rar"):
        logger.info("Processing RAR file.")
        try:
            with rarfile.RarFile(uploaded_file) as rar_ref:
                rar_ref.extractall(upload_directory)  # Extract directly to permanent directory
                logger.info(f"Extracted RAR to: {upload_directory}")
        except rarfile.BadRarFile:
            st.error("The uploaded RAR file is corrupted or not a valid RAR archive.")
            logger.warning("Bad RAR file uploaded.")
            st.stop()
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error: {e}")
            st.stop()

    # Handle single PDF or DOCX files
    elif uploaded_file.type == "application/pdf" or uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        logger.info(f"Saving file: {uploaded_file.name}")
        try:
            file_path = os.path.join(upload_directory, uploaded_file.name)
            with open(file_path, "wb") as file:
                file.write(uploaded_file.read())
        except Exception as e:
            st.error(f"Error saving the uploaded file: {e}")
            st.stop()

    else:
        st.error("Unsupported file type uploaded.")
        return

    # Display processing message
    processing_placeholder = st.empty()
    processing_placeholder.info("Processing the document(s)... Please wait.")

    # Process all files in the upload directory
    for idx, document in enumerate(os.listdir(upload_directory), 1):
        document_path = os.path.join(upload_directory, document)

        # Update the placeholder with the current processing file
        processing_placeholder.info(f"Processing File {idx}: `{os.path.basename(document_path)}`")
        logger.info(f"Processing file {idx}: {document_path}")

        try:
            # Process the document to extract status and keyword occurrences
            status, keyword_occurrences = process_tender_document(document_path)

            # LLM Processing Step
            llm_response = process_with_llm(status, keyword_occurrences, processing_model)

        except Exception as e:
            st.error(f"An error occurred while processing `{os.path.basename(document_path)}`: {e}")
            continue  # Skip to the next file

        # Display the document information and results
        st.markdown(f"### Processing File {idx}: `{os.path.basename(document_path)}`")
        st.markdown("#### Keywords and Reference Pages:")
        st.markdown(llm_response)
        st.markdown("<hr>", unsafe_allow_html=True)  # Separator between documents

    # Update the processing message to indicate completion
    processing_placeholder.success("✅ Processing completed!")
