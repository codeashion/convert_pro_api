from docx import Document


def word_to_html(input_path: str, output_path: str):
    document = Document(input_path)

    html_content = "<html><body>"

    for para in document.paragraphs:
        text = para.text.strip()
        if text:
            html_content += f"<p>{text}</p>"

    html_content += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
