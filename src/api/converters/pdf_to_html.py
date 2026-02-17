from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import BytesIO


def convert_pdf_to_html(input_pdf: str) -> str:
    output = BytesIO()

    with open(input_pdf, "rb") as pdf_file:
        extract_text_to_fp(
            pdf_file,
            output,
            laparams=LAParams(),
            output_type="html"
        )

    html_content = output.getvalue().decode("utf-8")
    return html_content
