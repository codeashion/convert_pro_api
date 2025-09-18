from sqlalchemy import Column, BigInteger, Integer, DateTime
from pydantic import BaseModel
from datetime import datetime
from ..database import Base

class FamilyMemberPoints(Base):
    __tablename__ = "family_member_points"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    family_member_id = Column(BigInteger, nullable=False)
    total_points = Column(Integer, default=0, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class FamilyMemberPointsCreate(BaseModel):
    family_member_id: int
    total_points: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

class FamilyMemberPointsOut(BaseModel):
    id: int
    user_id: int
    family_member_id: int
    total_points: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
