from sqlalchemy import Column, BigInteger, String, Text
from ..database import Base
from pydantic import BaseModel

class DailyQuote(Base):
	__tablename__ = "daily_quotes"
	id = Column(BigInteger, primary_key=True, autoincrement=True)
	type = Column(String(100), nullable=False)
	quote = Column(Text, nullable=False)

class DailyQuoteOut(BaseModel):
	id: int
	type: str
	quote: str

	class Config:
		orm_mode = True
