import pandas as pd


def excel_to_csv(input_path: str, output_path: str):
    # Read Excel file
    df = pd.read_excel(input_path)

    # Replace NaN with empty string
    df = df.fillna("")

    # Save as CSV
    df.to_csv(output_path, index=False)
