# import pdfplumber

# with pdfplumber.open("/home/cimcon/Downloads/BOQ_92829.pdf") as pdf:
#     for page in pdf.pages:
#         table = page.extract_table()
#         print(table)


# import pdfplumber
# import csv

# output_csv = "BOQ_1699917.csv"

# with pdfplumber.open("/home/cimcon/Downloads/BOQ_1699917.pdf") as pdf:
#     with open(output_csv, mode="w", newline="") as csvfile:
#         writer = csv.writer(csvfile)
#         for page in pdf.pages:
#             table = page.extract_table()
#             if table:  # Only process non-empty tables
#                 writer.writerows(table)

# print(f"Tables extracted and saved to {output_csv}")


import pandas as pd

def excel_to_csv(input_file, output_file):
    # Specify the engine explicitly
    df = pd.read_excel(input_file, engine='openpyxl')
    df.to_csv(output_file, index=False)

input_file = "/home/cimcon/Downloads/reference_df.xlsx"
output_file = "reference_df.csv"

excel_to_csv(input_file, output_file)
print("Conversion complete!")