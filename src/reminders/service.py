from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
from ..reminders.models import Reminder, ReminderCreate, ReminderUpdate, ReminderOut
from ..admin_users.models import FamilyMember
from ..auth import verify_token

def get_all_reminders(
    db: Session, 
    token: str, 
    limit: int = 100, 
    offset: int = 0,
    search: Optional[str] = None,
    active: Optional[bool] = None,
    family_member_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[ReminderOut]:
    """Get all reminders for the authenticated parent with optional filtering"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        # Start with base query
        query = select(Reminder, FamilyMember).join(
            FamilyMember, Reminder.family_member_id == FamilyMember.id
        ).where(Reminder.user_id == user_id)
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Reminder.title.like(search_pattern)) | 
                (Reminder.message.like(search_pattern))
            )
        
        # Apply active status filter
        if active is not None:
            query = query.where(Reminder.is_active == active)
            
        # Apply family member filter
        if family_member_id is not None:
            # First validate family member belongs to parent
            family_member = db.execute(
                select(FamilyMember).where(
                    and_(
                        FamilyMember.id == family_member_id,
                        FamilyMember.user_id == user_id
                    )
                )
            ).scalars().first()
            
            if not family_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Family member not found or doesn't belong to parent"
                )
            
            query = query.where(Reminder.family_member_id == family_member_id)
            
        # Apply date range filter
        if date_from:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            query = query.where(Reminder.reminder_date >= date_from_obj)
            
        if date_to:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            query = query.where(Reminder.reminder_date <= date_to_obj)
        
        # Apply ordering and pagination
        query = query.order_by(Reminder.reminder_date.desc(), Reminder.reminder_time.desc())
        query = query.limit(limit).offset(offset)
        
        reminders = db.execute(query).all()
        
        result = []
        for reminder, family_member in reminders:
            reminder_dict = {
                "id": reminder.id,
                "title": reminder.title,
                "reminder_date": reminder.reminder_date,
                "reminder_time": reminder.reminder_time,
                "repeat_pattern": reminder.repeat_pattern,
                "family_member_id": reminder.family_member_id,
                "family_member_name": family_member.member_name,
                "voice_note": reminder.voice_note,
                "message": reminder.message,
                "audio_file": reminder.audio_file,
                "is_active": reminder.is_active,
                "created_at": reminder.created_at,
                "updated_at": reminder.updated_at
            }
            
            result.append(ReminderOut(**reminder_dict))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminders: {str(e)}"
        )

def get_reminder_by_id(db: Session, token: str, reminder_id: int) -> ReminderOut:
    """Get a specific reminder by ID"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        result = db.execute(
            select(Reminder, FamilyMember)
            .join(FamilyMember, Reminder.family_member_id == FamilyMember.id)
            .where(
                and_(
                    Reminder.id == reminder_id,
                    Reminder.user_id == user_id
                )
            )
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        reminder, family_member = result
        
        reminder_dict = {
            "id": reminder.id,
            "title": reminder.title,
            "reminder_date": reminder.reminder_date,
            "reminder_time": reminder.reminder_time,
            "repeat_pattern": reminder.repeat_pattern,
            "family_member_id": reminder.family_member_id,
            "family_member_name": family_member.member_name,
            "voice_note": reminder.voice_note,
            "message": reminder.message,
            "audio_file": reminder.audio_file,
            "is_active": reminder.is_active,
            "created_at": reminder.created_at,
            "updated_at": reminder.updated_at
        }
        
        return ReminderOut(**reminder_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminder: {str(e)}"
        )

def create_reminder(db: Session, token: str, reminder_data: ReminderCreate) -> ReminderOut:
    """Create a new reminder"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        # Validate family member exists and belongs to user
        family_member = db.execute(
            select(FamilyMember)
            .where(
                and_(
                    FamilyMember.id == reminder_data.family_member_id,
                    FamilyMember.user_id == user_id
                )
            )
        ).scalars().first()
        
        if not family_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Family member not found or doesn't belong to user"
            )
        
        # Create reminder
        new_reminder = Reminder(
            user_id=user_id,
            title=reminder_data.title,
            reminder_date=reminder_data.reminder_date,
            reminder_time=reminder_data.reminder_time,
            repeat_pattern=reminder_data.repeat_pattern,
            family_member_id=reminder_data.family_member_id,
            voice_note=reminder_data.voice_note,
            message=reminder_data.message,
            audio_file=reminder_data.audio_file
        )
        
        db.add(new_reminder)
        db.commit()
        db.refresh(new_reminder)
        
        reminder_dict = {
            "id": new_reminder.id,
            "title": new_reminder.title,
            "reminder_date": new_reminder.reminder_date,
            "reminder_time": new_reminder.reminder_time,
            "repeat_pattern": new_reminder.repeat_pattern,
            "family_member_id": new_reminder.family_member_id,
            "family_member_name": family_member.member_name,
            "voice_note": new_reminder.voice_note,
            "message": new_reminder.message,
            "audio_file": new_reminder.audio_file,
            "is_active": new_reminder.is_active,
            "created_at": new_reminder.created_at,
            "updated_at": new_reminder.updated_at
        }
        
        return ReminderOut(**reminder_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reminder: {str(e)}"
        )

def update_reminder(db: Session, token: str, reminder_id: int, reminder_data: ReminderUpdate) -> ReminderOut:
    """Update an existing reminder"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        # Get existing reminder
        reminder = db.execute(
            select(Reminder)
            .where(
                and_(
                    Reminder.id == reminder_id,
                    Reminder.user_id == user_id
                )
            )
        ).scalars().first()
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        # Validate family member if provided
        if reminder_data.family_member_id is not None:
            family_member = db.execute(
                select(FamilyMember)
                .where(
                    and_(
                        FamilyMember.id == reminder_data.family_member_id,
                        FamilyMember.user_id == user_id
                    )
                )
            ).scalars().first()
            
            if not family_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Family member not found or doesn't belong to user"
                )
        
        # Update reminder fields
        update_data = reminder_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reminder, field, value)
        
        reminder.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(reminder)
        
        return get_reminder_by_id(db, token, reminder_id)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update reminder: {str(e)}"
        )

def delete_reminder(db: Session, token: str, reminder_id: int) -> dict:
    """Delete a reminder"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        reminder = db.execute(
            select(Reminder)
            .where(
                and_(
                    Reminder.id == reminder_id,
                    Reminder.user_id == user_id
                )
            )
        ).scalars().first()
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        db.delete(reminder)
        db.commit()
        
        return {
            "statusCode": 200,
            "status": True,
            "message": "Reminder deleted successfully",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reminder: {str(e)}"
        )

def get_upcoming_reminders(db: Session, token: str) -> list:
    """Get upcoming reminders for the next week, return title and formatted time string"""
    try:
        token_data = verify_token(token)
        user_id = int(token_data.get("id"))
        print("Decoded User ID:", user_id)
        now = datetime.now()
        today = now.date()
        next_week = today + timedelta(days=7)

        # Query for reminders from today to next week
        query = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.reminder_date >= today,
            Reminder.reminder_date <= next_week,
            Reminder.is_active == True
        ).order_by(Reminder.reminder_date.asc(), Reminder.reminder_time.asc())

        reminders = db.execute(query).scalars().all()
        result = []
        for reminder in reminders:
            # Only include today's reminders if time is after now
            if reminder.reminder_date == today and reminder.reminder_time <= now.time():
                continue
            # Get family member assigned color
            family_member = db.execute(
                select(FamilyMember).where(FamilyMember.id == reminder.family_member_id, FamilyMember.user_id == user_id)
            ).scalars().first()
            assigned_color = getattr(family_member, "assigned_colour", None) if family_member else None

            # Format time as '10:00 AM'
            time_str = reminder.reminder_time.strftime('%I:%M %p')

            reminder_dt = datetime.combine(reminder.reminder_date, reminder.reminder_time)
            day_name = reminder_dt.strftime('%A')
            if reminder.reminder_date == today:
                day_str = f"Today at {time_str}"
            elif reminder.reminder_date == today + timedelta(days=1):
                day_str = f"Tomorrow at {time_str}"
            else:
                day_str = f"{day_name}, {time_str}"
            date_str = reminder.reminder_date.strftime('%d %B %Y')
            result.append({
                "title": reminder.title,
                "time": time_str,
                "display": day_str,
                "assigned_colour": assigned_color,
                "date": date_str
            })
        return result 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve upcoming reminders: {str(e)}"
        )
        
def get_upcoming_monthly_reminders(db: Session, token: str) -> list:
    """Get upcoming reminders from today to end of month, same response as weekly"""
    try:
        token_data = verify_token(token)
        user_id = int(token_data.get("id"))
        print("Decoded User ID:", user_id)
        now = datetime.now()
        today = now.date()
        # Calculate end of month
        if today.month == 12:
            end_of_month = today.replace(day=31)
        else:
            from calendar import monthrange
            last_day = monthrange(today.year, today.month)[1]
            end_of_month = today.replace(day=last_day)

        # Query for reminders from today to end of month
        query = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.reminder_date >= today,
            Reminder.reminder_date <= end_of_month,
            Reminder.is_active == True
        ).order_by(Reminder.reminder_date.asc(), Reminder.reminder_time.asc())

        reminders = db.execute(query).scalars().all()
        result = []
        for reminder in reminders:
            # Only include today's reminders if time is after now
            if reminder.reminder_date == today and reminder.reminder_time <= now.time():
                continue
            # Get family member assigned color
            family_member = db.execute(
                select(FamilyMember).where(FamilyMember.id == reminder.family_member_id, FamilyMember.user_id == user_id)
            ).scalars().first()
            assigned_color = getattr(family_member, "assigned_colour", None) if family_member else None

            # Format time as '10:00 AM'
            time_str = reminder.reminder_time.strftime('%I:%M %p')

            reminder_dt = datetime.combine(reminder.reminder_date, reminder.reminder_time)
            day_name = reminder_dt.strftime('%A')
            if reminder.reminder_date == today:
                day_str = f"Today at {time_str}"
            elif reminder.reminder_date == today + timedelta(days=1):
                day_str = f"Tomorrow at {time_str}"
            else:
                day_str = f"{day_name}, {time_str}"
            date_str = reminder.reminder_date.strftime('%d %B %Y')
            result.append({
                "title": reminder.title,
                "time": time_str,
                "display": day_str,
                "assigned_colour": assigned_color,
                "date": date_str
            })
        return result 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve upcoming monthly reminders: {str(e)}"
        )       
        
        
        
def get_reminders_by_date(db: Session, token: str, date: str) -> list:
    """Get all reminders for a user on a specific date"""
    try:
        token_data = verify_token(token)
        user_id = int(token_data.get("id"))
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")

        query = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.reminder_date == date_obj
        ).order_by(Reminder.reminder_time.asc())

        reminders = db.execute(query).scalars().all()
        result = []
        for reminder in reminders:
            family_member = db.execute(
                select(FamilyMember).where(FamilyMember.id == reminder.family_member_id, FamilyMember.user_id == user_id)
            ).scalars().first()
            assigned_color = getattr(family_member, "assigned_colour", None) if family_member else None
            time_str = reminder.reminder_time.strftime('%I:%M %p')
            result.append({
                "id": reminder.id,
                "title": reminder.title,
                "reminder_date": reminder.reminder_date,
                "reminder_time": time_str,
                "repeat_pattern": reminder.repeat_pattern,
                "family_member_id": reminder.family_member_id,
                "assigned_colour": assigned_color,
                "voice_note": reminder.voice_note,
                "message": reminder.message,
                "audio_file": reminder.audio_file,
                "is_active": reminder.is_active,
                "created_at": reminder.created_at,
                "updated_at": reminder.updated_at
            })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminders by date: {str(e)}"
        )        
        