from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time, datetime
from ..database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    
    # Task scheduling
    task_date = Column(Date, nullable=False)
    task_time = Column(Time, nullable=False)
    repeat_pattern = Column(String(50), nullable=True)  # "none", "daily", "weekly", "monthly", "yearly"
    
    # Assignment and points
    points = Column(Integer, default=0)
    icon = Column(String(100), nullable=True)  # Icon identifier string
    
    # Privacy and reminders
    is_private = Column(Boolean, default=False)
    reminder_enabled = Column(Boolean, default=True)
    
    # Media and messages
    voice_note = Column(String(255), nullable=True)  # Voice note file path/string
    tone = Column(String(255), nullable=True)  # Tone file path/string
    message = Column(Text, nullable=True)
    audio_file = Column(String(255), nullable=True)  # Audio file path
    
    # Status and metadata
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    task_assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete")

class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    family_member_id = Column(Integer, ForeignKey("family_members.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="task_assignments")
    family_member = relationship("FamilyMember")

class TaskIcon(Base):
    __tablename__ = "task_icons"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(255), nullable=False)  # Half URL or file path
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Pydantic Models for API

class TaskAssignmentCreate(BaseModel):
    family_member_id: int

class TaskAssignmentOut(BaseModel):
    id: int
    family_member_id: int
    family_member_name: str
    assigned_at: datetime
    
    class Config:
        from_attributes = True

# TaskIcon Pydantic Models

class TaskIconCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=255)

class TaskIconUpdate(BaseModel):
    image_url: Optional[str] = Field(None, min_length=1, max_length=255)

class TaskIconOut(BaseModel):
    id: int
    image_url: str
    
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    task_date: date
    task_time: time
    repeat_pattern: Optional[str] = "none"
    points: Optional[int] = 0
    icon: Optional[str] = None
    is_private: Optional[bool] = False
    reminder_enabled: Optional[bool] = True
    voice_note: Optional[str] = None
    tone: Optional[str] = None
    message: Optional[str] = None
    audio_file: Optional[str] = None
    assigned_family_members: List[int] = []  # List of family member IDs

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    task_date: Optional[date] = None
    task_time: Optional[time] = None
    repeat_pattern: Optional[str] = None
    points: Optional[int] = None
    icon: Optional[str] = None
    is_private: Optional[bool] = None
    reminder_enabled: Optional[bool] = None
    voice_note: Optional[str] = None
    tone: Optional[str] = None
    message: Optional[str] = None
    audio_file: Optional[str] = None
    is_completed: Optional[bool] = None
    assigned_family_members: Optional[List[int]] = None



class TaskCompleteUpdate(BaseModel):
    is_completed: Optional[bool] = None

class TaskOut(BaseModel):
    id: int
    title: str
    task_date: date
    task_time: time
    repeat_pattern: Optional[str]
    points: int
    icon: Optional[str]
    is_private: bool
    reminder_enabled: bool
    voice_note: Optional[str]
    tone: Optional[str]
    message: Optional[str]
    audio_file: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    assigned_family_members: List[TaskAssignmentOut] = []
    
    class Config:
        from_attributes = True