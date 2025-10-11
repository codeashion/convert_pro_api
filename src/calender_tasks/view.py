from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..calender_tasks.service import get_calendar_tasks, get_month_tasks_reminders
from ..database import get_db

router = APIRouter(prefix="/calendar-tasks", tags=["calendar-tasks"])

@router.get("/family-members-tasks")
def family_members_tasks(db: Session = Depends(get_db), token: str = Header(...)):
	"""
	Get all family members for the user (from token) and their assigned tasks for today and next available date.
	"""
	return get_calendar_tasks(db, token)


@router.get("/calender-task-remainder")
def calender_task_remainder(
	db: Session = Depends(get_db),
	token: str = Header(...)
):
	"""
	Get date-wise full month tasks and reminders with family member details for the current month and year.
	"""
	from datetime import date
	today = date.today()
	year = today.year
	month = today.month
	return get_month_tasks_reminders(db, token, year, month)
