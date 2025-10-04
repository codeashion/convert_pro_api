from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func
from ..database import Base
from pydantic import BaseModel
from typing import Optional

class Photo(Base):
	__tablename__ = "photos"
	id = Column(BigInteger, primary_key=True, autoincrement=True)
	file = Column(String(255), nullable=False)
	created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
	updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class PhotoCreate(BaseModel):
	file: str

class PhotoUpdate(BaseModel):
	file: Optional[str] = None

from datetime import datetime

class PhotoOut(BaseModel):
	id: int
	file: str
	created_at: Optional[datetime]
	updated_at: Optional[datetime]

	class Config:
		orm_mode = True
