from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from ..database import Base

# SQLAlchemy model
class ShoppingItem(Base):
    __tablename__ = "home_essential"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_name = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models
class ShoppingItemCreate(BaseModel):
    item_name: str
    is_completed: Optional[bool] = False

class ShoppingItemOut(ShoppingItemCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
