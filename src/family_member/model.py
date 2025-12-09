from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import date
from ..database import Base

class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"))
    member_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    assigned_colour = Column(String(50))
    image_path = Column(String(255))
    voice_recording = Column(String(255))
    voice_id = Column(String(255))


# ---------- Pydantic Schemas ----------
class FamilyMemberCreate(BaseModel):
    member_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    assigned_colour: Optional[str] = None
    image_path: Optional[str] = None
    voice_recording: Optional[str] = None
    voice_id: Optional[str] = None

class FamilyMemberOut(FamilyMemberCreate):
    id: int

    class Config:
        orm_mode = True
