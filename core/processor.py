import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))

from core.text_extractor import extract_text_from_file
from core.keyword_mapper import map_keywords_to_categories
from core.keywords import PREDEFINED_KEYWORDS
from log.logger import setup_logger

logger = setup_logger("processor_logs")


# def process_tender_document(pdf_path):
    
#     logger.info(f"Processing tender document: {pdf_path}")
    
#     tender_documents = extract_text_from_pdf(pdf_path)
    
#     if not tender_documents:
        
#         logger.warning("No text found in the document.")
        
#         print("No text found in the document.")
#         return {
#             "Document Status": "Not Relevant",
#             "Categories": None
#         }, []
    
#     status, keyword_occurrences = map_keywords_to_categories(tender_documents, PREDEFINED_KEYWORDS)
    
#     logger.debug("Document processed successfully.")
    
#     return status, keyword_occurrences


def process_tender_document(file_path):
    logger.info(f"Processing tender document: {file_path}")
    
    # Use the unified extract_text_from_file function
    tender_documents = extract_text_from_file(file_path)

    if not tender_documents:
        logger.warning("No text found in the document.")
        return {
            "Document Status": "Not Relevant",
            "Categories": None
        }, []
    
    # Use existing keyword mapping logic
    status, keyword_occurrences = map_keywords_to_categories(tender_documents, PREDEFINED_KEYWORDS)
    
    logger.debug("Document processed successfully.")
    
    return status, keyword_occurrences
