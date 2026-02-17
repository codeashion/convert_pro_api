from PIL import Image, UnidentifiedImageError


def compress_image(input_path: str, output_path: str, quality: int):
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if image has transparency (PNG/WEBP)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.save(
                output_path,
                format="JPEG",
                quality=quality,
                optimize=True
            )

    except UnidentifiedImageError:
        raise ValueError("Invalid image file. Cannot identify image.")

    except Exception as e:
        raise ValueError(f"Image compression failed: {str(e)}")
