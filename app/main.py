import os
import sys
import streamlit as st  # type: ignore

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from modules.tender_classification import process_uploaded_file
from modules.chat_with_tender import chat_with_tender_interface
from modules.cost_estimation import tender_cost_estimation_interface


# from model.query_system import query_tender
from utils.file_utils import delete_all_files_and_directories



base_dir = os.path.dirname(os.path.abspath(__file__))
    

from log.logger import setup_logger


logger = setup_logger("app_logs")
    



def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
        
        

# Set the page configuration
st.set_page_config(
    page_title="Tender Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
st.sidebar.title("Navigation")

# Instructions or a welcome message in the sidebar
st.sidebar.write("""Choose an option below:""")

# Navigation options with icons
page = st.sidebar.selectbox(
    "Select a functionality",
    ["📄 Tender Classification", "💬 Chat with Tender", "Tender Cost Estimation"]
)





# Call the function to load the CSS
css_file_path = os.path.join(base_dir, "..", "styles", "styles.css")
load_css(css_file_path)





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
        process_uploaded_file(uploaded_file, UPLOAD_DIRECTORY)





elif page == "💬 Chat with Tender":

    st.markdown('<div class="title">💬 Chat with Tender</div>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a PDF, DOCX, or ZIP file",
        type=["pdf", "docx", "zip"],
        accept_multiple_files=False,
    )
    
    chat_with_tender_interface(base_dir, uploaded_file)
    
    
    
    
    
    
elif page == "Tender Cost Estimation":
    
     # Display title
    st.markdown('<div class="title">Tender Cost Estimation</div>', unsafe_allow_html=True)
    
    # uploaded_file = st.file_uploader("Upload a PDF for Tender Cost Estimation", type=["pdf"])
    
    # File uploader with support for both PDF and Excel files
    uploaded_file = st.file_uploader(
        "Upload a file for Tender Cost Estimation (PDF or Excel)",
        type=["pdf", "xls", "xlsx"]
    )
    
    reference_csv_path = os.path.join(base_dir, "..", "modules", "reference_df_mod.csv")
    
    tender_cost_estimation_interface(reference_csv_path, uploaded_file)
    
    
    
    

# Add a button to reset or clear data
if st.sidebar.button("Clear All Uploaded Data"):
    delete_all_files_and_directories()
    st.sidebar.success("All uploaded files have been cleared!")
    
    
st.sidebar.markdown('</div>', unsafe_allow_html=True)