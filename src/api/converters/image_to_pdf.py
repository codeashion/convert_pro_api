import os
from PIL import Image
from datetime import datetime


def image_to_pdf(input_path: str, output_path: str | None = None) -> str:
    """
    Convert an image file to PDF.

    :param input_path: Path of uploaded image
    :param output_path: Optional output PDF path
    :return: Output PDF path
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError("Input image file not found")

    # Open image and convert to RGB (required for PDF)
    image = Image.open(input_path).convert("RGB")

    # If output_path not provided, generate automatically
    if not output_path:
        filename = os.path.splitext(os.path.basename(input_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"src/storage/outputs/{filename}_{timestamp}.pdf"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save as PDF
    image.save(output_path, "PDF", resolution=100.0)

    return output_path
