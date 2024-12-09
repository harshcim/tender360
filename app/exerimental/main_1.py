import tempfile
import os
import re
import sys
import streamlit as st  # type: ignore
import zipfile  # Added to handle ZIP files
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv # type: ignore
from urllib.parse import quote
import shutil
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS # type: ignore
from langchain.chains import RetrievalQA

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# from model.query_system import query_tender
from utils.data_utils import load_data, split_data, save_embeddings
from utils.file_utils import save_uploaded_file, list_uploaded_files, delete_all_files_and_directories



# Load environment variables0
load_dotenv()   
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

base_dir = os.path.dirname(os.path.abspath(__file__))
    
processing_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, max_output_tokens=8192)

from log.logger import setup_logger
from core.processor import process_tender_document


# def preprocess_answer_with_hyperlinks(answer, pdf_path):
#     """
#     Replace page numbers in the LLM response with hyperlinks to the corresponding PDF pages.
#     """
#     def clean_pdf_path(path):
#         """
#         Cleans the PDF path by removing extra spaces and encoding special characters.
#         """
#         path = os.path.abspath(path.strip()) 
#         # path = path.strip()  # Remove leading/trailing whitespace
        
#         return quote(path)
    
#     def replace_page_numbers(match):
#         page_number = match.group(1)
#         print(page_number)
#         cleaned_pdf_path = clean_pdf_path(pdf_path)
#         hyperlink = f'<a href="file://{cleaned_pdf_path}#page={page_number}" target="_blank">{page_number}</a>'
#         return hyperlink

#     # Pattern to find page numbers
#     pattern = r'\bpage (\d+)\b'
#     return re.sub(pattern, replace_page_numbers, answer, flags=re.IGNORECASE)


def process_with_llm(status, keyword_occurrences,pdf_path):
    
    # Prepare the prompt with the document's status and keyword occurrences
    # prompt = f"Analyze the following document:\n\nStatus: {status}\nKeywords: {keyword_occurrences}"
    
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
        response = processing_model.invoke(processing_prompt)
        # print(response)
        # enhanced_response = preprocess_answer_with_hyperlinks(response.content, pdf_path)
        
        # return response.content
        return response.content
    
    except Exception as e:
        logger.error(f"Error during LLM processing: {e}")
        return "Error: Unable to process with LLM."



logger = setup_logger("app_logs")

# Set the page configuration
st.set_page_config(
    page_title="Tender Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# # Sidebar navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.selectbox("Go for other Options", ["Tender Classification", "Chat with Tender"])

# Sidebar navigation
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
st.sidebar.title("Navigation")

# Instructions or a welcome message in the sidebar
st.sidebar.write("""Choose an option below:""")

# Navigation options with icons
page = st.sidebar.selectbox(
    "Select a functionality",
    ["📄 Tender Classification", "💬 Chat with Tender"]
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
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f0f3f4;  /* Light background */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sidebar title */
    .sidebar .sidebar-content h1 {
        color: #2E86C1;
        font-size: 24px;
        text-align: center;
        padding-bottom: 10px;
        border-bottom: 2px solid #e3f2fd;
    }

    /* Sidebar button */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        margin-top: 10px;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0056b3;
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


# Conditional rendering based on page selection
if page == "📄 Tender Classification":

    # Title
    st.markdown('<div class="title">📄 Tender Document Analyzer</div>', unsafe_allow_html=True)

    # File uploader for PDF and ZIP files
    uploaded_file = st.file_uploader(
        "Upload a PDF, DOCX or ZIP Document",
        type=["pdf", "docx", "zip"],  # Updated to accept 'zip' files
        accept_multiple_files=False,
    )

    # Specify the permanent upload directory
    UPLOAD_DIRECTORY = os.path.join(base_dir, "..","data","permanent_upload_directory")

    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    if uploaded_file is not None:
        
        logger.info(f"Uploaded file: {uploaded_file.name}")
        
        # Define the permanent file path
        file_path = os.path.join(UPLOAD_DIRECTORY, uploaded_file.name)

        # Save the uploaded file to the permanent directory
        try:
            with open(file_path, "wb") as perm_file:
                perm_file.write(uploaded_file.read())
        except Exception as e:
            st.error(f"Error saving the uploaded file: {e}")
            st.stop()

        # List to track files for the current session
        current_session_files = []

        if uploaded_file.type == "application/zip" or uploaded_file.name.lower().endswith(".zip"):
            
            logger.info("Processing ZIP file.")
            
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(UPLOAD_DIRECTORY)  # Extract directly to permanent directory
                    extracted_files = zip_ref.namelist()
                    if not extracted_files:
                        st.error("The ZIP file is empty or could not be extracted.")
                        logger.warning("ZIP extraction yielded no files.")
                        st.stop()
                    # Add extracted files to current session list
                    for file in extracted_files:
                        current_session_files.append(os.path.join(UPLOAD_DIRECTORY, file))
                logger.info(f"Extracted ZIP to: {UPLOAD_DIRECTORY}")

            except zipfile.BadZipFile:
                st.error("The uploaded ZIP file is corrupted or not a valid ZIP archive.")
                logger.warning("Bad ZIP file uploaded.")
                st.stop()
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logger.error(f"Unexpected error: {e}")
                st.stop()

        elif uploaded_file.type == "application/pdf" or uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # If a single PDF or DOCX is uploaded
            current_session_files.append(file_path)
        else:
            st.error("Unsupported file type uploaded.")

        # Filter and process only the current session files
        if current_session_files:
            # Display processing message
            processing_placeholder = st.empty()
            processing_placeholder.info("Processing the document(s)... Please wait.")

            # Process each document file (PDF or DOCX)
            for idx, document in enumerate(current_session_files, 1):
                # Update the placeholder with the current processing file
                processing_placeholder.info(f"Processing File {idx} of {len(current_session_files)}: `{os.path.basename(document)}`")
                
                logger.info(f"Processing file {idx}: {document}")
                
                try:
                    status, keyword_occurrences = process_tender_document(document)
                    
                    # LLM Processing Step
                    llm_response = process_with_llm(status, keyword_occurrences, document)
                    
                except Exception as e:
                    st.error(f"An error occurred while processing {os.path.basename(document)}: {e}")
                    continue  # Skip to the next file

                # Display the document information and results
                st.markdown(f"### Processing File {idx}: `{os.path.basename(document)}`")

                # Display the LLM-Enhanced Output
                st.markdown("#### Keywords and Reference Pages:")
                st.markdown(llm_response)

                st.markdown("<hr>", unsafe_allow_html=True)  # Separator between documents


            # Update the processing message to indicate completion
            processing_placeholder.success("✅ Processing completed!")


elif page == "💬 Chat with Tender":

    st.markdown('<div class="title">💬 Chat with Tender</div>', unsafe_allow_html=True)

    # Display currently uploaded files
    st.subheader("Uploaded Files")
    uploaded_files = list_uploaded_files()

    if uploaded_files:
        st.write("Currently available files in the directory:")
        for file in uploaded_files:
            st.write(f"- {file}")
    else:
        st.write("No files currently uploaded.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a PDF, DOCX, or ZIP file",
        type=["pdf", "docx", "zip"],
        accept_multiple_files=False,
    )
    
    index_path = os.path.join(base_dir, "..","data","vector_store.faiss","index.faiss")
    
    index_embedding = os.path.join(base_dir, "..","data","vector_store.faiss")
    
    
    if uploaded_file:
        # Save the uploaded file
        save_uploaded_file(uploaded_file)
        
        st.success(f"File '{uploaded_file.name}' has been uploaded and stored.")

        # Trigger background processing if embeddings don't already exist
        if not os.path.exists(index_path):
            with st.spinner("Processing your files..."):
                documents = load_data()
                
                if documents:
                    text_chunks = split_data(documents)
                    save_embeddings(text_chunks)
                    st.success("You can now query the data.")
                else:
                    st.warning("No valid documents found to process.")
    else:
        st.write("Upload a file to create a knowledge base.")
                
                
    
    
    def load_embadding_data():
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/text-embedding-004")
        db = FAISS.load_local(index_embedding, embeddings, allow_dangerous_deserialization=True)
        return db
    
    
    rag_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.8, max_output_tokens=8192)
    
    
    
    if os.path.exists(index_path):
        # If vector database exists, proceed with querying

        rag_prompt = """ 
        You are a specialized assistant for analyzing tender documents with a focus on keyword identification and relevant content extraction. Your main goal is to answer user queries about the presence of specific keywords or provide brief explanations if requested. Make sure to adhere strictly to the user’s
        query and provide accurate answers based only on the content of the uploaded tender documents.

        Guidelines for Responding to Queries:

        1. **Keyword Mapping**:
            - If the user asks if a specific keyword (technical or non-technical) is present in the document, search only for that keyword.
            - If the keyword is found, confirm its presence and provide a brief context (one or two sentences) where it appears in the document.
            - If the keyword is not found, clearly state that the keyword is not present in the document. Do not include any unrelated content.
            - Avoid retrieving any additional content that is not directly related to the user's keyword query.

        2. **Brief Explanations & Document Information**:
            - If the user requests a summary, tender title, timeline chart, or specific brief information, provide a concise and relevant answer based on the requested content.
            - Keep the response short and to the point. Use bullet points if the explanation involves multiple items.

        3. **Response Tone and Relevance**:
            - Keep your responses precise, concise, and user-friendly.
            - If the user's query is out of the context of the tender documents, gently ask them to refocus their question on the provided content.
            - Base all responses strictly on the content of the tender document. Avoid any speculation or inclusion of external information.

        Examples of Queries and Expected Responses:
            - **For Keyword Presence**: If the user asks, 'Does this tender contain the keyword 'energy meter device'?', search for that exact keyword. If found, confirm its presence and provide a short explanation or context. If not, clearly state that it is not mentioned in the document.\n
            - **For Brief Explanations**: If the user asks for a summary or brief description, offer a concise overview without unnecessary details.

        4. **Handling Context and Accuracy**:
            - If the retrieved information does not match the user's query, inform them that the specific information might not be available in the tender document.
            - Ensure every response directly aligns with the user's request to maintain clarity and relevance.

        Response Format Guidelines:
            - **Bullet Points**: Use bullet points for clarity when listing multiple details or points.
            - **Direct Answers**: Provide direct answers if the query is about the presence or absence of specific keywords.
            - **Keep It Concise**: Stick to brief and relevant responses, maintaining focus on the user’s question.

        Now, provide the information requested strictly based on the content of the uploaded tender documents.

        Context: \n{context}\n
        Question: \n{question}\n

        """
        
        prompt = PromptTemplate(template=rag_prompt, input_variables=["context","question"])
        
        # embeddings = GoogleGenerativeAIEmbeddings(model = "models/text-embedding-004")
        
        # retriever = FAISS.load_local("data/vector_store.faiss", embeddings, allow_dangerous_deserialization=True)
        # retriever = retriever.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        
        db = load_embadding_data()
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=rag_model,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )
                
        # Query input box
        question = st.text_input("Ask a question related to the tender documents:")

        if question:
            with st.spinner("Fetching response..."):
                response = qa_chain.invoke({"query": question})
                st.write(response['result'])
    else:
        # If vector database does not exist, prompt the user to upload content
        st.warning("No Knowledgebase found. Please upload document.")
        
# Add a button to reset or clear data
if st.sidebar.button("Clear All Uploaded Data"):
    delete_all_files_and_directories()
    st.sidebar.success("All uploaded files have been cleared!")
    
st.sidebar.markdown('</div>', unsafe_allow_html=True)


