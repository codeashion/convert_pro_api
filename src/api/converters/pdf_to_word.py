from pdf2docx import Converter

def pdf_to_word(input_pdf: str, output_docx: str):
    """
    Convert PDF to Word document
    """
    cv = Converter(input_pdf)
    cv.convert(output_docx, start=0, end=None)
    cv.close()
