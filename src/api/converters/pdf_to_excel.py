import camelot
import pandas as pd
import os

def pdf_to_excel(input_pdf: str, output_excel: str):
    """
    Convert PDF tables to Excel file
    """
    tables = camelot.read_pdf(
        input_pdf,
        pages="all",
        flavor="stream"  # works well for most PDFs
    )

    if tables.n == 0:
        raise Exception("No tables found in PDF")

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        for i, table in enumerate(tables):
            table.df.to_excel(
                writer,
                sheet_name=f"Table_{i+1}",
                index=False,
                header=False
            )
