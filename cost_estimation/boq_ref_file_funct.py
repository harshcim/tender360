import pandas as pd  # For handling DataFrame operations
import pdfplumber    # For extracting tables from PDF files
import re    

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


def process_boq_pdf(pdf_path):
    # Step 1: Extract tables from the PDF and load directly into a DataFrame
    extracted_data = []  # List to store table data
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:  # Only process non-empty tables
                extracted_data.extend(table)

    # Convert extracted data into a DataFrame
    data = pd.DataFrame(extracted_data)

    # Step 2: Identify the header row
    header_row_index = data[data.isin(["Item Description"]).any(axis=1)].index[0]
    data.columns = data.iloc[header_row_index]  # Set header row as column names

    # Step 3: Exclude header row and filter relevant columns
    df = data[header_row_index + 1:]  # Skip the header row itself
    required_columns = ["Sl.\nNo.", "Item Description", "Quantity", "Units"]
    filtered_df = df[required_columns]

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