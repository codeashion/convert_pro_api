from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..database import Base

class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)  # Half URL
    file_type = Column(String(50), nullable=False)  # "audio", "image", "document", etc.
    file_size = Column(Integer, nullable=True)  # File size in bytes
    upload_category = Column(String(100), nullable=False)  # "task_icons", "task_audio", "reminder_audio", etc.
    created_at = Column(DateTime, default=func.now())

# Pydantic Models

class FileUploadOut(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_url: str  # Half URL
    file_type: str
    file_size: Optional[int]
    upload_category: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    id: int
    file_url: str  # Half URL
    
    class Config:
        from_attributes = True