from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from pydantic import BaseModel
from datetime import datetime
from ..database import Base


class CompletedTask(Base):
    __tablename__ = "completed_task"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    family_member_id = Column(BigInteger, nullable=True)
    point = Column(Integer, default=0, nullable=True)
    status = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    task_id = Column(BigInteger, nullable=True)

class CompletedTaskCreate(BaseModel):
    point: int = 0
    status: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    task_id: int | None = None

class CompletedTaskOut(BaseModel):
    id: int
    user_id: int
    family_member_id: int | None = None
    point: int = 0
    status: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    task_id: int | None = None

    class Config:
        from_attributes = True