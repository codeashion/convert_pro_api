import os
from fastapi import UploadFile, Request
from .model import ApiResponse
from ..converters.image_to_pdf import image_to_pdf
from ..converters.pdf_to_excel import pdf_to_excel
from ..converters.pdf_to_word import pdf_to_word
from ..converters.pdf_to_image import pdf_to_images
from ..converters.pdf_to_text import extract_text_from_pdf
from ..converters.pdf_to_html import convert_pdf_to_html
from ..converters.excel_to_pdf import excel_to_pdf
from ..converters.excel_to_csv import excel_to_csv
from ..converters.csv_to_excel import csv_to_excel
from ..converters.word_to_pdf import word_to_pdf
from ..converters.word_to_html import word_to_html
from ..converters.ppt_to_pdf import ppt_to_pdf
from ..converters.jpg_to_png import jpg_to_png
from ..converters.png_to_jpg import png_to_jpg
from ..converters.webp_to_jpg import webp_to_jpg
from ..converters.webp_to_png import webp_to_png
from ..converters.image_compressor import compress_image
from ..converters.mp3_to_wav import convert_mp3_to_wav
from ..converters.pdf_compressor import compress_pdf   
from fastapi import HTTPException

import shutil
from datetime import datetime

BASE_DIR = os.getcwd()
UPLOAD_DIR = "src/storage/uploads"
OUTPUT_DIR = "src/storage/outputs"
ALLOWED_PDF_TYPES = ["application/pdf"]

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
ALLOWED_CONTENT_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
]

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def image_to_pdf_service(
    file: UploadFile,
    request: Request
) -> ApiResponse:

    filename = file.filename
    name, _ = os.path.splitext(filename)

    output_filename = f"{name}_{int(__import__('time').time())}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Save uploaded image
    input_path = os.path.join("src/storage/uploads", filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Convert
    image_to_pdf(input_path, output_path)

    # ✅ Build PUBLIC URL
    download_url = f"{request.base_url}downloads/{output_filename}"

    return ApiResponse(
        status="success",
        message="Image converted to PDF successfully",
        data={
            "input_file": filename,
            "output_file": output_filename,
            "download_url": download_url
        }
    )


async def pdf_to_excel_service(file: UploadFile, base_url: str) -> ApiResponse:
    if file.content_type not in ALLOWED_PDF_TYPES:
        return ApiResponse(
            status="error",
            message="Only PDF files are allowed"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    input_path = os.path.join(
        UPLOAD_DIR,
        f"{timestamp}_{file.filename}"
    )

    output_filename = file.filename.replace(".pdf", f"_{timestamp}.xlsx")
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pdf_to_excel(input_path, output_path)

    download_url = f"{base_url}/downloads/{output_filename}"

    return ApiResponse(
        status="success",
        message="PDF converted to Excel successfully",
        data={
            "input_file": file.filename,
            "output_file": output_filename,
            "download_url": download_url
        }
    )
    
   
async def pdf_to_word_service(file: UploadFile, base_url: str) -> ApiResponse:
    if file.content_type not in ALLOWED_PDF_TYPES:
        return ApiResponse(
            status="error",
            message="Only PDF files are allowed"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    input_path = os.path.join(
        UPLOAD_DIR,
        f"{timestamp}_{file.filename}"
    )

    output_filename = file.filename.replace(".pdf", f"_{timestamp}.docx")
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pdf_to_word(input_path, output_path)

    download_url = f"{base_url}/downloads/{output_filename}"

    return ApiResponse(
        status="success",
        message="PDF converted to Word successfully",
        data={
            "input_file": file.filename,
            "output_file": output_filename,
            "download_url": download_url
        }
    )
    
    
async def pdf_to_image_service(file: UploadFile, base_url: str) -> ApiResponse:
    if file.content_type not in ALLOWED_PDF_TYPES:
        return ApiResponse(
            status="error",
            message="Only PDF files are allowed"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    input_path = os.path.join(
        UPLOAD_DIR,
        f"{timestamp}_{file.filename}"
    )

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    base_filename = file.filename.replace(".pdf", f"_{timestamp}")

    image_paths = pdf_to_images(
        input_pdf=input_path,
        output_dir=OUTPUT_DIR,
        base_filename=base_filename
    )

    download_urls = [
        f"{base_url}/downloads/{os.path.basename(path)}"
        for path in image_paths
    ]

    return ApiResponse(
        status="success",
        message="PDF converted to images successfully",
        data={
            "input_file": file.filename,
            "total_pages": len(download_urls),
            "images": download_urls
        }
    )
        
        
async def pdf_to_text_service(file: UploadFile, base_url: str) -> ApiResponse:
    if file.content_type != "application/pdf":
        return ApiResponse(
            status="error",
            message="Only PDF files are allowed"
        )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    input_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.filename}")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    extracted_text = extract_text_from_pdf(input_path)

    output_filename = f"{os.path.splitext(file.filename)[0]}_{timestamp}.txt"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return ApiResponse(
        status="success",
        message="PDF text extracted successfully",
        data={
            "input_file": file.filename,
            "output_file": output_filename,
            "text_preview": extracted_text[:500],  # first 500 chars
            "download_url": f"{base_url}/downloads/{output_filename}"
        }
    )
    

async def pdf_to_html_service(file: UploadFile, base_url: str) -> ApiResponse:
    if file.content_type != "application/pdf":
        return ApiResponse(
            status="error",
            message="Only PDF files are allowed"
        )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    input_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.filename}")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    html_content = convert_pdf_to_html(input_path)

    output_filename = f"{os.path.splitext(file.filename)[0]}_{timestamp}.html"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return ApiResponse(
        status="success",
        message="PDF converted to HTML successfully",
        data={
            "input_file": file.filename,
            "output_file": output_filename,
            "download_url": f"{base_url}/downloads/{output_filename}"
        }
    )        


def convert_excel_to_pdf(input_path: str, output_path: str):
    excel_to_pdf(input_path, output_path)


def convert_excel_to_csv(input_path: str, output_path: str):
    excel_to_csv(input_path, output_path)


def convert_csv_to_excel(input_path: str, output_path: str):
    csv_to_excel(input_path, output_path)

def convert_word_to_pdf(input_path: str, output_path: str):
    word_to_pdf(input_path, output_path)

def convert_word_to_html(input_path: str, output_path: str):
    word_to_html(input_path, output_path)

def convert_ppt_to_pdf(input_path: str, output_path: str):
    ppt_to_pdf(input_path, output_path)

def convert_jpg_to_png(input_path: str, output_path: str):
    jpg_to_png(input_path, output_path)

def convert_png_to_jpg(input_path: str, output_path: str):
    png_to_jpg(input_path, output_path)

def convert_webp_to_jpg(input_path: str, output_path: str):
    webp_to_jpg(input_path, output_path)

def convert_webp_to_png(input_path: str, output_path: str):
    webp_to_png(input_path, output_path)

def compress_image_service_logic(input_path: str, output_path: str, quality: int):
    compress_image(input_path, output_path, quality)


def compress_image_service_logic(input_path: str, output_path: str, quality: int, filename: str, content_type: str):
    
    # Validate quality
    if quality < 1 or quality > 100:
        raise HTTPException(
            status_code=400,
            detail="Quality must be between 1 and 100"
        )

    # Validate extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed"
        )

    # Validate MIME type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image."
        )

    try:
        compress_image(input_path, output_path, quality)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

def mp3_to_wav_service_logic(input_path: str, output_path: str, filename: str, content_type: str):

    # Validate extension
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".mp3":
        raise HTTPException(
            status_code=400,
            detail="Only MP3 files are allowed."
        )

    # Validate MIME type
    if content_type not in ["audio/mpeg", "audio/mp3"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a valid MP3 file."
        )

    try:
        convert_mp3_to_wav(input_path, output_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))    
    



def compress_pdf_service_logic(input_path: str, output_path: str, quality: str, filename: str):

    # Validate extension
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    try:
        compress_pdf(input_path, output_path, quality)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

