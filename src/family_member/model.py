from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import date

Base = declarative_base()

class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    member_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    assigned_colour = Column(String)
    image_path = Column(String)
    voice_recording = Column(String)


# ---------- Pydantic Schemas ----------
class FamilyMemberCreate(BaseModel):
    member_name: str
    date_of_birth: date
    assigned_colour: Optional[str]
    image_path: Optional[str]
    voice_recording: Optional[str]

class FamilyMemberOut(FamilyMemberCreate):
    id: int

    class Config:
        orm_mode = True
