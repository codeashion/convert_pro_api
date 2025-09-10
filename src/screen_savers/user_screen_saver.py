from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database import Base

class UserScreenSaver(Base):
    __tablename__ = "user_screen_savers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    screen_saver_id = Column(Integer, ForeignKey("screen_savers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

# Pydantic Schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserScreenSaverCreate(BaseModel):
    screen_saver_id: int

class UserScreenSaverOut(BaseModel):
    id: int
    user_id: int
    screen_saver_id: int
    created_at: Optional[datetime]
    class Config:
        orm_mode = True
