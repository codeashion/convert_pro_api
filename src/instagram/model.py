from sqlalchemy import Column, Integer, Text, Date, Time, DateTime, SmallInteger, func
from ..database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class Instagram(Base):
	__tablename__ = "instagram"
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, nullable=False)
	image = Column(Text, nullable=False)
	date = Column(Date, nullable=False)
	time = Column(Time, nullable=False)
	caption = Column(Text, nullable=True)
	created_at = Column(DateTime, server_default=func.current_timestamp())
	updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
	post_status = Column(SmallInteger, default=0)

class InstagramCreate(BaseModel):
	image: str
	date: date
	time: time
	caption: Optional[str] = None
	post_status: Optional[int] = 0
	# user_id is set from token, not required from client

class InstagramUpdate(BaseModel):
	image: Optional[str] = None
	date: Optional[str] = None  # Accept string for date (e.g., '2025-10-06')
	time: Optional[str] = None  # Accept string for time (e.g., '15:27:00')
	caption: Optional[str] = None
	post_status: Optional[int] = None

class InstagramOut(BaseModel):
	id: int
	user_id: int
	image: str
	date: date
	time: time
	caption: Optional[str]
	created_at: Optional[datetime]
	updated_at: Optional[datetime]
	post_status: int

	class Config:
		orm_mode = True
