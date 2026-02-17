import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch


def excel_to_pdf(input_path: str, output_path: str):

    # Read Excel
    df = pd.read_excel(input_path)

    # Replace NaN with empty string
    df = df.fillna("")

    data = [df.columns.tolist()] + df.values.tolist()

    # Landscape A4
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,  
        bottomMargin=20,
    )

    elements = []

    # Calculate column widths dynamically
    page_width = landscape(A4)[0] - 40  # page width minus margins
    col_count = len(df.columns)
    col_width = page_width / col_count

    table = Table(data, colWidths=[col_width] * col_count)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ])

    table.setStyle(style)
    elements.append(table)

    pdf.build(elements)
