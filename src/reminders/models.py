from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from ..database import Base

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    
    # Reminder scheduling
    reminder_date = Column(Date, nullable=False)
    reminder_time = Column(Time, nullable=False)
    repeat_pattern = Column(String(50), nullable=True)  # "none", "daily", "weekly", "monthly", "yearly"
    
    # Assignment
    family_member_id = Column(Integer, ForeignKey("family_members.id", ondelete="CASCADE"), nullable=False)
    
    # Media and messages
    voice_note = Column(String(255), nullable=True)  # Voice note file path/string
    message = Column(Text, nullable=True)
    audio_file = Column(String(255), nullable=True)  # Audio file path
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    family_member = relationship("FamilyMember")

# Pydantic Models for API

class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    reminder_date: date
    reminder_time: time
    repeat_pattern: Optional[str] = "none"
    family_member_id: int
    voice_note: Optional[str] = None
    message: Optional[str] = None
    audio_file: Optional[str] = None

class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    reminder_date: Optional[date] = None
    reminder_time: Optional[time] = None
    repeat_pattern: Optional[str] = None
    family_member_id: Optional[int] = None
    voice_note: Optional[str] = None
    message: Optional[str] = None
    audio_file: Optional[str] = None
    is_active: Optional[bool] = None

class ReminderOut(BaseModel):
    id: int
    title: str
    reminder_date: date
    reminder_time: time
    repeat_pattern: Optional[str]
    family_member_id: int
    family_member_name: str
    voice_note: Optional[str]
    message: Optional[str]
    audio_file: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True