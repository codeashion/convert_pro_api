from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional
import os
import uuid
from pathlib import Path
import mimetypes
from ..file_upload.models import FileUpload, FileUploadOut, FileUploadResponse

# Allowed file types and categories
ALLOWED_EXTENSIONS = {
    'audio': ['.mp3', '.wav', '.m4a', '.ogg', '.flac'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'],
    'document': ['.pdf', '.doc', '.docx', '.txt']
}
 
UPLOAD_CATEGORIES = {
    'task_icons': 'uploads/task_icons',
    'task_audio': 'uploads/task_audio', 
    'reminder_audio': 'uploads/reminder_audio',
    'profile_images': 'uploads/profile_images',
    'documents': 'uploads/documents',
    'screen_savers': 'uploads/screen_savers'
}

def get_file_type(filename: str) -> str:
    """Determine file type based on extension"""
    file_extension = Path(filename).suffix.lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if file_extension in extensions:
            return file_type
    
    return 'unknown'

def validate_file(file: UploadFile, category: str) -> str:
    """Validate uploaded file and return file type"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_type = get_file_type(file.filename)
    
    if file_type == 'unknown':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )
    
    # Category-specific validation
    if category == 'task_icons' and file_type != 'image':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task icons must be image files"
        )
    
    if category in ['task_audio', 'reminder_audio'] and file_type != 'audio':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio files required for audio uploads"
        )
    
    return file_type

async def save_uploaded_file(
    db: Session,
    file: UploadFile,
    category: str
) -> FileUploadResponse:
    """Save uploaded file and return file info"""
    try:
        # Validate file
        file_type = validate_file(file, category)
        
        # Check if category exists
        if category not in UPLOAD_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid upload category: {category}"
            )
        
        # Create directory if it doesn't exist
        upload_dir = Path(UPLOAD_CATEGORIES[category])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        stored_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / stored_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Create half URL (relative path)
        file_url = f"/{UPLOAD_CATEGORIES[category]}/{stored_filename}"
        
        # Save to database
        file_record = FileUpload(
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_url=file_url,
            file_type=file_type,
            file_size=len(content),
            upload_category=category
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        return FileUploadResponse(
            id=file_record.id,
            file_url=file_record.file_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if database save fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

def get_file_by_id(db: Session, file_id: int) -> FileUploadOut:
    """Get file information by ID"""
    try:
        file_record = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return FileUploadOut.from_orm(file_record)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve file: {str(e)}"
        )

def delete_file(db: Session, file_id: int) -> dict:
    """Delete file and its record"""
    try:
        file_record = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete physical file
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        
        # Delete database record
        db.delete(file_record)
        db.commit()
        
        return {
            "statusCode": 200,
            "status": True,
            "message": "File deleted successfully",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

def seed_preloaded_files(db: Session) -> None:
    """Seed database with pre-uploaded files"""
    try:
        # Check if files already seeded
        existing_files = db.query(FileUpload).filter(
            FileUpload.upload_category == 'preloaded'
        ).first()
        
        if existing_files:
            return  # Already seeded
        
        # Define pre-uploaded files
        preloaded_files = [
            # Add your actual pre-uploaded files here
            # Example: {
            #     'original_filename': 'actual-avatar.png',
            #     'stored_filename': 'actual-avatar.png',
            #     'file_path': 'uploads/profile_images/actual-avatar.png',
            #     'file_url': '/uploads/profile_images/actual-avatar.png',
            #     'file_type': 'image',
            #     'upload_category': 'profile_images',
            #     'file_size': 0
            # }
        ]
        
        for file_data in preloaded_files:
            # Check if file actually exists
            if os.path.exists(file_data['file_path']):
                file_record = FileUpload(
                    original_filename=file_data['original_filename'],
                    stored_filename=file_data['stored_filename'],
                    file_path=file_data['file_path'],
                    file_url=file_data['file_url'],
                    file_type=file_data['file_type'],
                    file_size=file_data['file_size'],
                    upload_category=file_data['upload_category']
                )
                db.add(file_record)
        
        db.commit()
        print(f"Seeded {len(preloaded_files)} pre-uploaded files")
        
    except Exception as e:
        db.rollback()
        print(f"Failed to seed pre-uploaded files: {str(e)}")