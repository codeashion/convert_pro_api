import os
from pdf2image import convert_from_path

POPPLER_PATH = r"D:\poppler-25.12.0\Library\bin"

def pdf_to_images(input_pdf: str, output_dir: str, base_filename: str):
    if not os.path.isfile(input_pdf):
        raise FileNotFoundError("Input PDF not found")

    images = convert_from_path(
        pdf_path=input_pdf,
        dpi=200,
        fmt="png",
        poppler_path=POPPLER_PATH
    )

    saved_files = []

    for i, image in enumerate(images, start=1):
        filename = f"{base_filename}_page_{i}.png"
        output_path = os.path.join(output_dir, filename)
        image.save(output_path, "PNG")
        saved_files.append(output_path)

    return saved_files
