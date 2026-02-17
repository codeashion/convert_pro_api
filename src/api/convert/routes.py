from fastapi import APIRouter, UploadFile, File, Request
from .service import image_to_pdf_service, pdf_to_excel_service, pdf_to_word_service, pdf_to_image_service, pdf_to_text_service, pdf_to_html_service, compress_image_service_logic, compress_pdf_service_logic
from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
router = APIRouter()


UPLOAD_DIR = "src/storage/uploads"
OUTPUT_DIR = "src/storage/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/image-to-pdf")
async def image_to_pdf(
    request: Request,
    file: UploadFile = File(...)
):
    return await image_to_pdf_service(file, request)

@router.post("/pdf-to-excel")
async def pdf_to_excel(
    request: Request,
    file: UploadFile = File(...)
):
    base_url = str(request.base_url).rstrip("/")
    return await pdf_to_excel_service(file, base_url)

@router.post("/pdf-to-word")
async def pdf_to_word(
    request: Request,
    file: UploadFile = File(...)
):
    base_url = str(request.base_url).rstrip("/")
    return await pdf_to_word_service(file, base_url)

@router.post("/pdf-to-image")
async def pdf_to_image(
    request: Request,
    file: UploadFile = File(...)
):
    base_url = str(request.base_url).rstrip("/")
    return await pdf_to_image_service(file, base_url)

@router.post("/pdf-to-text")
async def pdf_to_text(request: Request, file: UploadFile = File(...)):
    base_url = str(request.base_url).rstrip("/")
    return await pdf_to_text_service(file, base_url)

@router.post("/pdf-to-html")
async def pdf_to_html(request: Request, file: UploadFile = File(...)):
    base_url = str(request.base_url).rstrip("/")
    return await pdf_to_html_service(file, base_url)

@router.post("/excel-to-pdf")
async def excel_to_pdf_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".xlsx", ".pdf")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_excel_to_pdf
    convert_excel_to_pdf(input_path, output_path)

    # Build download URL
    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "File converted successfully",
        "download_url": download_url
    }


@router.post("/excel-to-csv")
async def excel_to_csv_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".xlsx", ".csv")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_excel_to_csv
    convert_excel_to_csv(input_path, output_path)

    # Create download URL
    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "Excel converted to CSV successfully",
        "download_url": download_url
    }


@router.post("/csv-to-excel")
async def csv_to_excel_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".csv", ".xlsx")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_csv_to_excel
    convert_csv_to_excel(input_path, output_path)

    # Create download URL
    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "CSV converted to Excel successfully",
        "download_url": download_url
    }


@router.post("/word-to-pdf")
async def word_to_pdf_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".docx", ".pdf")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_word_to_pdf
    convert_word_to_pdf(input_path, output_path)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "Word converted to PDF successfully",
        "download_url": download_url
    }

@router.post("/word-to-html")
async def word_to_html_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".docx", ".html")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_word_to_html
    convert_word_to_html(input_path, output_path)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "Word converted to HTML successfully",
        "download_url": download_url
    }

@router.post("/ppt-to-pdf")
async def ppt_to_pdf_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".pptx", ".pdf").replace(".ppt", ".pdf")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_ppt_to_pdf
    convert_ppt_to_pdf(input_path, output_path)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "PowerPoint converted to PDF successfully",
        "download_url": download_url
    }

@router.post("/jpg-to-png")
async def jpg_to_png_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = (
        file.filename.replace(".jpg", ".png")
                     .replace(".jpeg", ".png")
                     .replace(".JPG", ".png")
                     .replace(".JPEG", ".png")
    )
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_jpg_to_png
    convert_jpg_to_png(input_path, output_path)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "JPG converted to PNG successfully",
        "download_url": download_url
    }

@router.post("/png-to-jpg")
async def png_to_jpg_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".png", ".jpg").replace(".PNG", ".jpg")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_png_to_jpg
    convert_png_to_jpg(input_path, output_path)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "PNG converted to JPG successfully",
        "download_url": download_url
    }


@router.post("/webp-to-jpg")
async def webp_to_jpg_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".webp", ".jpg").replace(".WEBP", ".jpg")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_webp_to_jpg
    convert_webp_to_jpg(input_path, output_path)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "WEBP converted to JPG successfully",
        "download_url": download_url
    }


@router.post("/webp-to-png")
async def webp_to_png_api(request: Request, file: UploadFile = File(...)):
    input_path = f"src/storage/uploads/{file.filename}"
    output_filename = file.filename.replace(".webp", ".png").replace(".WEBP", ".png")
    output_path = f"src/storage/outputs/{output_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    from src.api.convert.service import convert_webp_to_png
    convert_webp_to_png(input_path, output_path)

    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/storage/outputs/{output_filename}"

    return {
        "message": "WEBP converted to PNG successfully",
        "download_url": download_url
    }

@router.post("/compress-image")
async def compress_image_api(
    file: UploadFile = File(...),
    quality: int = Query(75)
):
    import uuid
    import shutil
    import os

    unique_id = str(uuid.uuid4())

    input_path = os.path.join(UPLOAD_DIR, f"{unique_id}_{file.filename}")
    output_filename = f"{unique_id}_compressed.jpg"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🔥 FIXED CALL
    compress_image_service_logic(
        input_path=input_path,
        output_path=output_path,
        quality=quality,
        filename=file.filename,
        content_type=file.content_type
    )

    download_url = f"http://localhost:8000/static/outputs/{output_filename}"

    return {
        "message": "Image compressed successfully",
        "download_url": download_url
    }

@router.post("/mp3-to-wav")
async def mp3_to_wav_api(file: UploadFile = File(...)):

    import uuid
    import shutil
    import os

    unique_id = str(uuid.uuid4())

    input_path = os.path.join(UPLOAD_DIR, f"{unique_id}_{file.filename}")
    output_filename = f"{unique_id}.wav"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call service
    from src.api.convert.service import mp3_to_wav_service_logic
    mp3_to_wav_service_logic(
        input_path=input_path,
        output_path=output_path,
        filename=file.filename,
        content_type=file.content_type
    )

    download_url = f"http://localhost:8000/static/outputs/{output_filename}"

    return {
        "message": "MP3 converted to WAV successfully",
        "download_url": download_url
    }


@router.post("/compress-pdf")
async def compress_pdf_api(
    file: UploadFile = File(...),
    quality: str = Query("ebook")
):

    import uuid
    import shutil
    import os

    unique_id = str(uuid.uuid4())

    input_path = os.path.join(UPLOAD_DIR, f"{unique_id}_{file.filename}")
    output_filename = f"{unique_id}_compressed.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call service
    compress_pdf_service_logic(
        input_path=input_path,
        output_path=output_path,
        quality=quality,
        filename=file.filename
    )

    download_url = f"http://localhost:8000/static/outputs/{output_filename}"

    return {
        "message": "PDF compressed successfully",
        "quality": quality,
        "download_url": download_url6
    }

