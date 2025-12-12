from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date
from ..database import Base

# ---------------------------
# SQLAlchemy Models
# ---------------------------

class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=True)  # Nullable for social login users
    profile_image = Column(String(255), nullable=True)  # Optional profile image URL/path

    # Social login fields
    google_id = Column(String(100), nullable=True, unique=True)
    apple_id = Column(String(100), nullable=True, unique=True)
    provider = Column(String(20), nullable=True)  # 'email', 'google', 'apple'

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete")
    tasks = relationship("Task", back_populates="user", cascade="all, delete")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"))
    member_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    assigned_colour = Column(String(50))
    image_path = Column(String(255))
    voice_id = Column(String(255))
    voice_recording = Column(String(255))

    user = relationship("User", back_populates="family_members")


# ---------------------------
# Pydantic Schemas
# ---------------------------

# ---- FamilyMember ----
class FamilyMemberCreate(BaseModel):
    member_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    assigned_colour: Optional[str] = None 
    voice_id : Optional[str] = None
    image_path: Optional[str] = None
    voice_recording: Optional[str] = None


class FamilyMemberOut(FamilyMemberCreate):
    id: int

    class Config:
        orm_mode = True


# ---- User ----
class UserCreate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    confirm_password: Optional[str] = None
    profile_image: Optional[str] = None
    family_members: Optional[List[FamilyMemberCreate]] = Field(default_factory=list)

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


# Firebase Login Models
class FirebaseLoginRequest(BaseModel):
    id_token: str  # Firebase ID token


class FirebaseLoginResponse(BaseModel):
    statusCode: int = 200
    status: bool = True
    message: str
    data: dict


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    profile_image: Optional[str] = None
    family_members: List[FamilyMemberOut] = []

    class Config:
        orm_mode = True


# Alias/derivative for clarity in API schemas
class ParentOut(UserOut):
    pass

from datetime import datetime
from typing import Optional

class LeaderboardMemberOut(BaseModel):
    id: int
    family_member_id: int
    member_name: str
    image_path: Optional[str]
    date_of_birth: Optional[datetime]
    assigned_colour: Optional[str]
    voice_recording: Optional[str]
    total_points: int

    class Config:
        from_attributes = True
