from fastapi import APIRouter, Depends, File, UploadFile, Form, Header
from sqlalchemy.orm import Session
from ..file_upload.service import save_uploaded_file
from ..file_upload.models import FileUploadResponse
from ..database import get_db
from ..auth import verify_token

router = APIRouter(prefix="/upload", tags=["file-upload"])

@router.post("/", response_model=FileUploadResponse)
async def upload_file_endpoint(
    category: str = Form(...),  # task_icons, task_audio, reminder_audio, profile_images, documents
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Global file upload endpoint

    Categories:
    - task_icons: For task icon images
    - task_audio: For task audio files
    - reminder_audio: For reminder audio files
    - profile_images: For parent profile images
    - documents: For document uploads
    """
    # Token authentication removed; endpoint is now public
    return await save_uploaded_file(db, file, category)
