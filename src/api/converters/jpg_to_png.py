from PIL import Image


def jpg_to_png(input_path: str, output_path: str):
    with Image.open(input_path) as img:
        rgb_image = img.convert("RGB")  # Ensure correct format
        rgb_image.save(output_path, "PNG")
