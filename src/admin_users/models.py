from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    member_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    assigned_colour = Column(String)
    image_path = Column(String)
    voice_recording = Column(String)

    user = relationship("User", back_populates="family_members")

# ---------------------------
# Pydantic Schemas
# ---------------------------

# ---- FamilyMember ----
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

# ---- User ----
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str = Field(min_length=6)
    confirm_password: str
    family_members: List[FamilyMemberCreate]

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    family_members: List[FamilyMemberOut] = []

    class Config:
        orm_mode = True
