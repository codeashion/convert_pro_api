import pandas as pd

def csv_to_excel(input_path: str, output_path: str):
    # Read CSV
    df = pd.read_csv(input_path)

    # Replace NaN with empty string
    df = df.fillna("")

    # Save as Excel
    df.to_excel(output_path, index=False, engine="openpyxl")
