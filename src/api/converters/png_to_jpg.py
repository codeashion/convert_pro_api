from PIL import Image


def png_to_jpg(input_path: str, output_path: str):
    with Image.open(input_path) as img:
        # Convert transparent background to white
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            background.save(output_path, "JPEG", quality=95)
        else:
            img.convert("RGB").save(output_path, "JPEG", quality=95)
