from PIL import Image


def webp_to_png(input_path: str, output_path: str):
    with Image.open(input_path) as img:
        # Preserve transparency if exists
        img.save(output_path, "PNG")
