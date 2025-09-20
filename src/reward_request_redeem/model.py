from sqlalchemy import Column, BigInteger, Integer, String, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from ..database import Base

class RewardRequestRedeem(Base):
	__tablename__ = "reward_request_redeem"

	id = Column(BigInteger, primary_key=True, index=True)
	name = Column(String(255), nullable=False)
	points = Column(Integer, nullable=False, default=0)
	request_date = Column(Date, nullable=True)
	redeem_date = Column(Date, nullable=True)
	family_member_id = Column(BigInteger, ForeignKey("family_members.id"), nullable=False)
	redeem_status = Column(Integer, nullable=False, default=0)
	reward_id = Column(BigInteger, ForeignKey("rewards.id"), nullable=False)
	created_at = Column(TIMESTAMP, server_default=func.now())
	updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# Pydantic Schemas
class RewardRequestRedeemCreate(BaseModel):
	name: str = Field(..., max_length=255)
	points: int = 0
	family_member_id: int
	reward_id: int

class RewardRequestRedeemUpdate(BaseModel):
	redeem_date: Optional[date] = None
	redeem_status: Optional[int] = None

class RewardRequestRedeemOut(BaseModel):
	id: int
	name: str
	points: int
	request_date: Optional[date]
	redeem_date: Optional[date]
	family_member_id: int
	redeem_status: int
	reward_id: int
	created_at: Optional[datetime]
	updated_at: Optional[datetime]

	class Config:
		from_attributes = True
		orm_mode = True
