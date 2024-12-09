import os
import shutil
import streamlit as st # type: ignore
import zipfile


base_dir = os.path.dirname(os.path.abspath(__file__))  # This gets the path of the utils directory

# Directory path for storing uploaded files
# classification_upload_directory = "./permanent_upload_directory"
classification_upload_directory = os.path.join(base_dir, "..","data", "permanent_upload_directory")

# UPLOAD_DIR = "./data/uploaded_files/"
UPLOAD_DIR = os.path.join(base_dir, "..","data", "uploaded_files") 

# VECTOR_DB_PATH = "./data/vector_store.faiss/"
VECTOR_DB_PATH = os.path.join(base_dir, "..","data", "vector_store.faiss")




def ensure_upload_dir_exists():
    """Check if the upload directory exists; if not, create it."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
        

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to the upload directory."""
    ensure_upload_dir_exists()
    
    # Check if the uploaded file is a ZIP file
    if uploaded_file.type == "application/zip":
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            # Extract PDF and DOCX files from any nested folders to the root directory
            for file_name in zip_ref.namelist():
                if file_name.endswith(('.pdf', '.docx')):
                    # Get the file's base name (remove any directory path)
                    base_name = os.path.basename(file_name)
                    # Construct the full path to save in the upload directory
                    save_path = os.path.join(UPLOAD_DIR, base_name)
                    
                    # Extract and save the file directly to UPLOAD_DIR
                    with zip_ref.open(file_name) as source, open(save_path, "wb") as target:
                        shutil.copyfileobj(source, target)
        return f"Extracted files from {uploaded_file.name}"
    
    # For non-ZIP files, save directly to the directory
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    
    return file_path




def list_uploaded_files():
    """List files available in the upload directory."""
    ensure_upload_dir_exists()
    return os.listdir(UPLOAD_DIR)




def ensure_vector_db_exists():
    """Ensure the vector database directory exists."""
    if not os.path.exists(VECTOR_DB_PATH):
        os.makedirs(VECTOR_DB_PATH)
        
        
        

def delete_all_files_and_directories():
    """Delete uploaded files and vector database, then recreate necessary directories."""
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)  # Deletes the uploaded files directory
    if os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)  # Deletes the vector database
    if os.path.exists(classification_upload_directory):
        shutil.rmtree(classification_upload_directory) 
    
    os.makedirs(classification_upload_directory)
    os.makedirs(UPLOAD_DIR)  # Recreate empty uploaded files directory
    ensure_vector_db_exists()  # Recreate vector database directory if needed