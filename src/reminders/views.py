from fastapi import Body
from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..reminders.service import (
    get_all_reminders, get_reminder_by_id, create_reminder, update_reminder, 
    delete_reminder, get_upcoming_reminders, get_upcoming_monthly_reminders
)
from ..reminders.service import get_reminders_by_date
from ..reminders.models import ReminderCreate, ReminderUpdate, ReminderOut
from ..database import get_db

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.get("/", response_model=List[ReminderOut])
def get_reminders_endpoint(
    limit: int = 100, 
    offset: int = 0,
    search: Optional[str] = None,  # Search in title or message
    active: Optional[bool] = None,  # Filter by active status
    family_member_id: Optional[int] = None,  # Filter by family member
    date_from: Optional[str] = None,  # Filter by date range (YYYY-MM-DD)
    date_to: Optional[str] = None,  # Filter by date range (YYYY-MM-DD)
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Get all reminders with optional search and filtering"""
    return get_all_reminders(db, token, limit, offset, search, active, family_member_id, date_from, date_to)

@router.post("/by-date", response_model=List[dict])
def get_reminders_by_date_endpoint(
    db: Session = Depends(get_db),
    token: str = Header(...),
    date: str = Body(..., embed=True, example="2025-10-15")
):
    """Get all reminders for a user on a specific date"""
    return get_reminders_by_date(db, token, date)

@router.get("/upcoming", response_model=List[dict])
def get_upcoming_reminders_endpoint(
    db: Session = Depends(get_db),
    token: str = Header(...)
):
    """Get upcoming reminders for the next week (title and formatted time only)"""
    return get_upcoming_reminders(db, token)

@router.get("/upcoming-monthly", response_model=List[dict])
def get_upcoming_monthly_reminders_endpoint(
    db: Session = Depends(get_db),
    token: str = Header(...)
):
    """Get upcoming reminders for the rest of the month (title, time, color, date, display)"""
    return get_upcoming_monthly_reminders(db, token)

@router.get("/{reminder_id}", response_model=ReminderOut)
def get_reminder_endpoint(
    reminder_id: int, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Get a specific reminder by ID"""
    return get_reminder_by_id(db, token, reminder_id)

@router.post("/add", response_model=ReminderOut)
def create_reminder_endpoint(
    reminder_data: ReminderCreate, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Create a new reminder"""
    return create_reminder(db, token, reminder_data)

@router.put("/{reminder_id}", response_model=ReminderOut)
def update_reminder_endpoint(
    reminder_id: int, 
    reminder_data: ReminderUpdate, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Update an existing reminder"""
    return update_reminder(db, token, reminder_id, reminder_data)

@router.delete("/{reminder_id}")
def delete_reminder_endpoint(
    reminder_id: int, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Delete a reminder"""
    return delete_reminder(db, token, reminder_id)
