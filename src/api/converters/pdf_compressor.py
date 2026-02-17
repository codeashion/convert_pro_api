import subprocess


def compress_pdf(input_path: str, output_path: str, quality: str):
    """
    quality options:
    - screen      (lowest size, lowest quality)
    - ebook       (medium quality)
    - printer     (high quality)
    - prepress    (very high quality)
    - default     (balanced)
    """

    quality_settings = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress",
        "default": "/default"
    }

    if quality not in quality_settings:
        raise ValueError("Invalid quality option.")

    try:
        subprocess.run(
            [
                "gswin64c",  # Windows
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={quality_settings[quality]}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_path}",
                input_path,
            ],
            check=True,
        )
    except subprocess.CalledProcessError:
        raise ValueError("PDF compression failed.")
