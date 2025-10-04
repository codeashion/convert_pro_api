from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..calender_tasks.service import get_calendar_tasks
from ..database import get_db

router = APIRouter(prefix="/calendar-tasks", tags=["calendar-tasks"])

@router.get("/family-members-tasks")
def family_members_tasks(db: Session = Depends(get_db), token: str = Header(...)):
	"""
	Get all family members for the user (from token) and their assigned tasks for today and next available date.
	"""
	return get_calendar_tasks(db, token)
