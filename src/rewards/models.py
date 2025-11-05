from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..database import Base


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False) 
    reward = Column(String(255), nullable=False)
    points = Column(String(100), nullable=False)
    requested_by = Column(String(255), nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class RewardCreate(BaseModel):
    reward: str = Field(min_length=1, max_length=255)
    points: str = Field(min_length=1, max_length=100)
    requested_by: Optional[str] = None
    created_by: Optional[str] = None


class RewardUpdate(BaseModel):
    reward: Optional[str] = Field(None, min_length=1, max_length=255)
    points: Optional[str] = Field(None, min_length=1, max_length=100)
    requested_by: Optional[str] = None
    created_by: Optional[str] = None


class RewardOut(BaseModel):
    id: int
    reward: str
    points: str
    requested_by: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


