import os
import sys
import logging

def setup_logger(script_name):    
    
    # Create a logger with the script name
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.DEBUG)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv_path = os.path.join(current_dir, "..","centralised_logs.log")
    handler = logging.FileHandler(input_csv_path)
    
    formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    handler.setFormatter(formatter)
    
    # Add the handler to the logger
    if not logger.hasHandlers():
        logger.addHandler(handler)
    
    return logger
