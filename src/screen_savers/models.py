from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from datetime import datetime
from ..database import Base


class ScreenSaver(Base):
    __tablename__ = "screen_savers"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=func.now())


class ScreenSaverCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=500)


class ScreenSaverUpdate(BaseModel):
    image_url: str = Field(min_length=1, max_length=500)


class ScreenSaverOut(BaseModel):
    id: int
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


