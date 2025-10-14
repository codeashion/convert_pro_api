from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from ..database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScreenSaver(Base):
	__tablename__ = "screen_savers"
	id = Column(Integer, primary_key=True, autoincrement=True)
	image_url = Column(String(500), nullable=False)
	created_at = Column(DateTime)
	user_id = Column(Integer, nullable=False)
	select_status = Column(SmallInteger, default=0)

class ScreenSaverCreate(BaseModel):
	image_url: str
	select_status: Optional[int] = 0

class ScreenSaverOut(BaseModel):
	id: int
	image_url: str
	created_at: Optional[datetime]
	user_id: int
	select_status: int

	class Config:
		orm_mode = True
