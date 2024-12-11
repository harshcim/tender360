import tempfile
import os
import re
import sys
import json
import pdfplumber  
import pandas as pd
import streamlit as st  # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv # type: ignore

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))



# Load environment variables0
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
estimating_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, max_output_tokens=8192)

from log.logger import setup_logger


def extract_reference_data(file_path):
    # Load the reference data from CSV
    df = pd.read_csv(file_path)
    
    # Clean the column names (remove any unwanted spaces or special characters)
    df.columns = df.columns.str.replace('\n', '').str.strip()
    
    # Assuming the columns are named 'Component Name' and 'Price' in the CSV
    reference_components = df[['Item Name', 'Selling Price/Nos']].to_dict('records')
    
    # Convert to formatted string
    reference_data_str = "\n".join(
        [f"- {i+1}. {item['Item Name']} - Price: {item['Selling Price/Nos']}" for i, item in enumerate(reference_components)]
    )
    
    return reference_components, reference_data_str


# def process_boq_pdf(pdf_path):
#     # Step 1: Extract tables from the PDF and load directly into a DataFrame
#     extracted_data = []  # List to store table data
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             table = page.extract_table()
#             if table:  # Only process non-empty tables
#                 extracted_data.extend(table)

#     # Convert extracted data into a DataFrame
#     data = pd.DataFrame(extracted_data)

#     # Step 2: Identify the header row
#     header_row_index = data[data.isin(["Item Description"]).any(axis=1)].index[0]
#     data.columns = data.iloc[header_row_index]  # Set header row as column names

#     # Step 3: Exclude header row and filter relevant columns
#     df = data[header_row_index + 1:]  # Skip the header row itself
#     required_columns = ["Sl.\nNo.", "Item Description", "Quantity", "Units"]
#     filtered_df = df[required_columns]

#     # Step 4: Create a list of dictionaries
#     boq_components = []
#     for idx, row in filtered_df.iterrows():
#         if pd.notna(row['Sl.\nNo.']) and pd.notna(row['Item Description']):
#             boq_components.append({
#                 "Sl.No": row['Sl.\nNo.'],
#                 "Description": row['Item Description'],
#                 "Quantity": row['Quantity'],
#                 "Unit": row['Units']
#             })

#     # Step 5: Format the BOQ data into a structured string
#     boq_data_str = "\n".join(
#         [f"- {item['Sl.No']}. {item['Description']} ({item['Quantity']} {item['Unit'] if item['Quantity'] else ''})"
#          for item in boq_components]
#     )

#     return boq_data_str


def process_boq(file_path):
    # Step 1: Determine file type and load data into a DataFrame
    if file_path.endswith(('.pdf', '.PDF')):
        # PDF processing
        extracted_data = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    extracted_data.extend(table)
        data = pd.DataFrame(extracted_data)
    elif file_path.endswith(('.xls', '.xlsx')):
        # Excel processing
        data = pd.read_excel(file_path, header=None)  # Load without headers
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or Excel file.")

    # Step 2: Identify the header row
    header_row_index = data[data.isin(["Item Description"]).any(axis=1)].index[0]
    data.columns = data.iloc[header_row_index]  # Set header row as column names

    # Step 3: Exclude header row and filter relevant columns
    df = data[header_row_index + 1:]  # Skip the header row itself
    required_columns = ["Sl.\nNo.", "Item Description", "Quantity", "Units"]
    try:
        filtered_df = df[required_columns]
    except KeyError:
        raise KeyError("One or more required columns are missing in the data.")

    # Step 4: Create a list of dictionaries
    boq_components = []
    for idx, row in filtered_df.iterrows():
        if pd.notna(row['Sl.\nNo.']) and pd.notna(row['Item Description']):
            boq_components.append({
                "Sl.No": row['Sl.\nNo.'],
                "Description": row['Item Description'],
                "Quantity": row['Quantity'],
                "Unit": row['Units']
            })

    # Step 5: Format the BOQ data into a structured string
    boq_data_str = "\n".join(
        [f"- {item['Sl.No']}. {item['Description']} ({item['Quantity']} {item['Unit'] if item['Quantity'] else ''})"
         for item in boq_components]
    )

    return boq_data_str


def tender_cost_estimation_interface(reference_csv_path, uploaded_file):
    """
    Interface for tender cost estimation.
    Args:
        base_dir (str): The base directory of the project.
        uploaded_file: Uploaded file for cost estimation.
    """

    if st.button("Estimate Cost"):
        if uploaded_file is not None:
            # Step 1: Save the uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            # Step 2: Process the uploaded PDF to extract data
            boq_data_str = process_boq(file_path)

            # Extract reference data
            reference_data_str = extract_reference_data(reference_csv_path)

            # Step 3: Construct the prompt
            estimating_prompt = f"""
            Task:  
            You are an assistant tasked with mapping components from a BOQ file to a reference list of components based on semantic similarity. 
            Your goal is to identify the most relevant reference component for each BOQ item, considering technical descriptions, quantities, and hierarchical relationships.

            Inputs:  
            1. Reference Components:  
            {reference_data_str}

            2. BOQ Components:  
            {boq_data_str}

            Rules:  
            - Match components based on technical descriptions and semantic similarity.  
            - Include hierarchical groupings for sub-items (e.g., 31 -> 31.01, 31.02).  
            - Handle units like MT, No, Nos, LT, KM, mtr, Year, LOT, Job, and similar.  
            - If no unit is mentioned, assume the default selling price as the first available reference component's price.  
            - Strictly take note: **Only return matched components**. Do not include any components with `"Mapped Reference Component": "Not Found"`. 

            Output Format Example:
            {{  
                "BOQ Component": "Providing and laying in position cement concrete",  
                "Quantity": "288.00",  
                "Unit": "cum",  
                "Mapped Reference Component": "Cement Concrete Mix",  
                "Unit Price": 1200.00,  
                "Total Cost": 345600.00     
            }},
            {{  
                "BOQ Component": "Cables (2 Core 1.5sq.mm.)",  
                "Quantity": "200.00",  
                "Unit": "M",  
                "Mapped Reference Component": "Cables (2 Core 1.5sq.mm.)",  
                "Unit Price": 50.00,  
                "Total Cost": 10000.00  
            }}
            """

            # Step 4: Call the model to get the response
            response = estimating_model.invoke(estimating_prompt)

            # Parse the model's response
            result = response.content.replace('```', '').replace('json', '')
            try:    
                result = json.loads(result)
            except json.JSONDecodeError:
                st.error("Failed to parse model response. Please check the model's output format.")
                return

            # Step 5: Convert the result to a DataFrame
            if result:
                df = pd.DataFrame(result)

                # Step 6: Calculate the total cost
                df['Total Cost'] = df['Unit Price'] * df['Quantity'].astype(float)

                # Calculate the total tender cost
                total_tender_cost = df['Total Cost'].sum()

                # Step 7: Display the result
                st.write("Estimated Tender Cost:")
                st.write(df)
                st.write(f"Total Estimated Tender Cost: {total_tender_cost:.2f}")
            else:
                st.error("No result returned from the model. Please check the input data.")
        else:
            st.warning("Please upload a file first!")