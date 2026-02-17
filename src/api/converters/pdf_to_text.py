from pypdf import PdfReader


def extract_text_from_pdf(input_pdf: str) -> str:
    reader = PdfReader(input_pdf)

    full_text = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text.append(text)

    return "\n\n".join(full_text)
