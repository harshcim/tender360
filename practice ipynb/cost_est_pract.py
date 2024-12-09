import pandas as pd

# Load the Excel file without assuming headers
file_path = "/home/cimcon/Desktop/Tender Usecases/Data/BOQ/BOQ_436332.xls"
data = pd.read_excel(file_path, header=None)  # Read all rows as plain data

# Define the desired column names
desired_columns = ["Sl.No.", "Item Description", "Quantity", "Units"]

header_row_index = data[data.isin(["Item Description"]).any(axis=1)].index[0]
data.columns = data.iloc[header_row_index]

# Step 3: Exclude header row and filter relevant columns
df = data[header_row_index + 1:]  # Skip the header row itself
required_columns = ["Sl.\nNo.", "Item Description", "Quantity", "Units"]
filtered_df = df[required_columns]
# print(filtered_df.head())

output_file = "processed_data.csv"
filtered_df.to_csv(output_file, index=False)


# # Search for the row containing the desired headers
# header_row_index = None

# print("Searching for the desired header row...")
# for i, row in data.iterrows():
#     # Strip spaces and normalize row values for comparison
#     normalized_row = row.astype(str).str.strip().str.replace("\n", " ")
#     if all(col in normalized_row.values for col in desired_columns):
#         header_row_index = i
#         print(f"Header found at row index {header_row_index}: {list(normalized_row)}")
#         break

# if header_row_index is not None:
#     # Set the identified row as the header
#     data.columns = data.iloc[header_row_index].str.strip().str.replace("\n", " ")
#     data = data.iloc[header_row_index + 1:]  # Exclude the header row itself from the data

#     # Keep only the desired columns
#     try:
#         data = data[desired_columns]
#     except KeyError as e:
#         print(f"Error: One or more of the desired columns were not found: {e}")
#         exit()

#     # Reset the index
#     data.reset_index(drop=True, inplace=True)

#     # Save the processed data to a CSV file
#     output_file = "processed_data.csv"
#     data.to_csv(output_file, index=False)
#     print(f"Processed data has been saved to {output_file}")
# else:
#     print("The specified headers were not found in the file. Please check the file format or column names.")
