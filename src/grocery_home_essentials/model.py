from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..database import Base

# SQLAlchemy model for Grocery & Home Essentials List (One per user)
class UserGroceryHomeEssential(Base):
    __tablename__ = "user_grocery_home_essentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)  # One list per user
    home_essential_ids = Column(String(500), default="")  # Comma-separated IDs
    grocery_ids = Column(String(500), default="")  # Comma-separated IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models for API (User-specific)
class UserGroceryHomeEssentialCreate(BaseModel):
    home_essential_ids: List[int] = []
    grocery_ids: List[int] = []

class UserGroceryHomeEssentialUpdate(BaseModel):
    home_essential_ids: Optional[List[int]] = None
    grocery_ids: Optional[List[int]] = None

class ItemDetails(BaseModel):
    id: int
    name: str

class UserGroceryHomeEssentialOut(BaseModel):
    id: int
    home_essentials: List[ItemDetails] = []
    groceries: List[ItemDetails] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True