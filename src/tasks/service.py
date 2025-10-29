from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, date
from ..tasks.models import Task, TaskAssignment, TaskCreate, TaskUpdate, TaskOut, TaskAssignmentOut, TaskIcon, TaskIconCreate, TaskIconUpdate, TaskIconOut
from ..admin_users.models import FamilyMember
from ..auth import verify_token
import logging

logger = logging.getLogger(__name__)

def get_all_tasks(
    db: Session,
    token: str,
    date: str,
    family_member_id: Optional[int] = None
) -> List[TaskOut]:
    """Get all tasks for the authenticated parent filtered by date (required) and family member (optional)"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])

        from datetime import datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()

        # Start with base query: filter by user and date
        query = select(Task).where(Task.user_id == user_id, Task.task_date == date_obj)

        # Apply ordering
        query = query.order_by(Task.task_time.desc())

        tasks = db.execute(query).scalars().all()

        result = []
        for task in tasks:
            # Get assigned family members
            assignments = db.execute(
                select(TaskAssignment, FamilyMember)
                .join(FamilyMember, TaskAssignment.family_member_id == FamilyMember.id)
                .where(TaskAssignment.task_id == task.id)
            ).all()

            assigned_members = [
                TaskAssignmentOut(
                    id=assignment.id,
                    family_member_id=assignment.family_member_id,
                    family_member_name=member.member_name,
                    assigned_at=assignment.assigned_at
                )
                for assignment, member in assignments
            ]

            # Apply family member filter if specified
            if family_member_id is not None:
                if not any(am.family_member_id == family_member_id for am in assigned_members):
                    continue

            task_dict = {
                "id": task.id,
                "title": task.title,
                "task_date": task.task_date,
                "task_time": task.task_time,
                "repeat_pattern": task.repeat_pattern,
                "points": task.points,
                "icon": task.icon,
                "is_private": task.is_private,
                "reminder_enabled": task.reminder_enabled,
                "voice_note": task.voice_note,
                "tone": task.tone,
                "message": task.message,
                "audio_file": task.audio_file,
                "is_completed": task.is_completed,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "assigned_family_members": assigned_members
            }

            result.append(TaskOut(**task_dict))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )

def get_task_by_id(db: Session, token: str, task_id: int) -> TaskOut:
    """Get a specific task by ID"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        task = db.execute(
            select(Task)
            .where(and_(Task.id == task_id, Task.user_id == user_id))
        ).scalars().first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Get assigned family members
        assignments = db.execute(
            select(TaskAssignment, FamilyMember)
            .join(FamilyMember, TaskAssignment.family_member_id == FamilyMember.id)
            .where(TaskAssignment.task_id == task.id)
        ).all()
        
        assigned_members = [
            TaskAssignmentOut(
                id=assignment.id,
                family_member_id=assignment.family_member_id,
                family_member_name=member.member_name,
                assigned_at=assignment.assigned_at
            )
            for assignment, member in assignments
        ]
        
        task_dict = {
            "id": task.id,
            "title": task.title,
            "task_date": task.task_date,
            "task_time": task.task_time,
            "repeat_pattern": task.repeat_pattern,
            "points": task.points,
            "icon": task.icon,
            "is_private": task.is_private,
            "reminder_enabled": task.reminder_enabled,
            "voice_note": task.voice_note,
            "tone": task.tone,
            "message": task.message,
            "audio_file": task.audio_file,
            "is_completed": task.is_completed,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "assigned_family_members": assigned_members
        }
        
        return TaskOut(**task_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task: {str(e)}"
        )

def create_task(db: Session, token: str, task_data: TaskCreate) -> TaskOut:
    """Create a new task"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        # Validate family members exist and belong to user
        if task_data.assigned_family_members:
            family_members = db.execute(
                select(FamilyMember)
                .where(
                    and_(
                        FamilyMember.id.in_(task_data.assigned_family_members),
                        FamilyMember.user_id == user_id
                    )
                )
            ).scalars().all()
            
            if len(family_members) != len(task_data.assigned_family_members):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some family members not found or don't belong to user"
                )
        

        # Repeat logic
        from datetime import timedelta
        repeat_mode = task_data.repeat_pattern
        start_date = task_data.task_date
        created_tasks = []
        repeat_limits = {
            "Daily": 30,      # create for next 30 days
            "Weekly": 12,     # create for next 12 weeks
            "Monthly": 12,    # create for next 12 months
            "Yearly": 5       # create for next 5 years
        }

        def add_task_for_date(task_date):
            new_task = Task(
                user_id=user_id,
                title=task_data.title,
                task_date=task_date,
                task_time=task_data.task_time,
                repeat_pattern=task_data.repeat_pattern,
                points=task_data.points,
                icon=task_data.icon,
                is_private=task_data.is_private,
                reminder_enabled=task_data.reminder_enabled,
                voice_note=task_data.voice_note,
                tone=task_data.tone,
                message=task_data.message,
                audio_file=task_data.audio_file
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            created_tasks.append(new_task)

            # If reminder_enabled, create a reminder
            if task_data.reminder_enabled:
                from ..reminders.models import Reminder
                reminder = Reminder(
                    title=task_data.title,
                    reminder_date=task_date,
                    reminder_time=task_data.task_time,
                    repeat_pattern=task_data.repeat_pattern,
                    family_member_id=task_data.assigned_family_members[0] if task_data.assigned_family_members else None,
                    message=task_data.message,
                    voice_note=task_data.voice_note,
                    audio_file=task_data.audio_file,
                    is_active=True
                )
                db.add(reminder)
                db.commit()
                db.refresh(reminder)

            # Create task assignments
            assigned_members = []
            if task_data.assigned_family_members:
                for family_member_id in task_data.assigned_family_members:
                    assignment = TaskAssignment(
                        task_id=new_task.id,
                        family_member_id=family_member_id
                    )
                    db.add(assignment)
                    assigned_members.append(assignment)
                db.commit()
            return new_task

        # Create tasks based on repeat mode
        if repeat_mode == "None" or not repeat_mode:
            add_task_for_date(start_date)
        elif repeat_mode == "Daily":
            for i in range(repeat_limits["Daily"]):
                add_task_for_date(start_date + timedelta(days=i))
        elif repeat_mode == "Weekly":
            for i in range(repeat_limits["Weekly"]):
                add_task_for_date(start_date + timedelta(weeks=i))
        elif repeat_mode == "Monthly":
            for i in range(repeat_limits["Monthly"]):
                month = (start_date.month - 1 + i) % 12 + 1
                year = start_date.year + ((start_date.month - 1 + i) // 12)
                day = min(start_date.day, [31,
                    29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
                from datetime import date as dt_date
                add_task_for_date(dt_date(year, month, day))
        elif repeat_mode == "Yearly":
            for i in range(repeat_limits["Yearly"]):
                year = start_date.year + i
                month = start_date.month
                day = start_date.day
                from datetime import date as dt_date
                add_task_for_date(dt_date(year, month, day))

        # Prepare response for the first created task
        first_task = created_tasks[0]
        # Get assigned member details for the first task
        assignments = db.execute(
            select(TaskAssignment, FamilyMember)
            .join(FamilyMember, TaskAssignment.family_member_id == FamilyMember.id)
            .where(TaskAssignment.task_id == first_task.id)
        ).all()
        assigned_member_details = [
            TaskAssignmentOut(
                id=assignment.id,
                family_member_id=assignment.family_member_id,
                family_member_name=member.member_name,
                assigned_at=assignment.assigned_at
            )
            for assignment, member in assignments
        ]

        task_dict = {
            "id": first_task.id,
            "title": first_task.title,
            "task_date": first_task.task_date,
            "task_time": first_task.task_time,
            "repeat_pattern": first_task.repeat_pattern,
            "points": first_task.points,
            "icon": first_task.icon,
            "is_private": first_task.is_private,
            "reminder_enabled": first_task.reminder_enabled,
            "voice_note": first_task.voice_note,
            "tone": first_task.tone,
            "message": first_task.message,
            "audio_file": first_task.audio_file,
            "is_completed": first_task.is_completed,
            "created_at": first_task.created_at,
            "updated_at": first_task.updated_at,
            "assigned_family_members": assigned_member_details
        }

        return TaskOut(**task_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

def update_task(db: Session, token: str, task_id: int, task_data: TaskUpdate) -> TaskOut:
    """Update an existing task"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        # Get existing task
        task = db.execute(
            select(Task)
            .where(and_(Task.id == task_id, Task.user_id == user_id))
        ).scalars().first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Validate family members if provided
        if task_data.assigned_family_members is not None:
            if task_data.assigned_family_members:
                family_members = db.execute(
                    select(FamilyMember)
                    .where(
                        and_(
                            FamilyMember.id.in_(task_data.assigned_family_members),
                            FamilyMember.user_id == user_id
                        )
                    )
                ).scalars().all()
                
                if len(family_members) != len(task_data.assigned_family_members):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Some family members not found or don't belong to user"
                    )
        
        # Update task fields
        update_data = task_data.dict(exclude_unset=True, exclude={"assigned_family_members"})
        for field, value in update_data.items():
            setattr(task, field, value)
        
        task.updated_at = datetime.utcnow()
        
        # Update assignments if provided
        if task_data.assigned_family_members is not None:
            # Delete existing assignments
            db.execute(
                select(TaskAssignment).where(TaskAssignment.task_id == task_id)
            )
            db.query(TaskAssignment).filter(TaskAssignment.task_id == task_id).delete()
            
            # Create new assignments
            for family_member_id in task_data.assigned_family_members:
                assignment = TaskAssignment(
                    task_id=task.id,
                    family_member_id=family_member_id
                )
                db.add(assignment)
        
        db.commit()
        db.refresh(task)
        
        return get_task_by_id(db, token, task_id)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )

def delete_task(db: Session, token: str, task_id: int) -> dict:
    """Delete a task"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        task = db.execute(
            select(Task)
            .where(and_(Task.id == task_id, Task.user_id == user_id))
        ).scalars().first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        db.delete(task)
        db.commit()
        
        return {
            "statusCode": 200,
            "status": True,
            "message": "Task deleted successfully",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )

# TaskIcon CRUD Functions

def get_all_task_icons(
    db: Session, 
    limit: int = 100, 
    offset: int = 0
) -> List[TaskIconOut]:
    """Get all task icons"""
    try:
        query = select(TaskIcon)
        
        # Apply ordering and pagination
        query = query.order_by(TaskIcon.id.asc())
        query = query.limit(limit).offset(offset)
        
        icons = db.execute(query).scalars().all()
        
        return [TaskIconOut.from_orm(icon) for icon in icons]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task icons: {str(e)}"
        )

def get_task_icon_by_id(db: Session, icon_id: int) -> TaskIconOut:
    """Get a specific task icon by ID"""
    try:
        icon = db.execute(
            select(TaskIcon).where(TaskIcon.id == icon_id)
        ).scalars().first()
        
        if not icon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task icon not found"
            )
        
        return TaskIconOut.from_orm(icon)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task icon: {str(e)}"
        )

def create_task_icon(db: Session, icon_data: TaskIconCreate) -> TaskIconOut:
    """Create a new task icon"""
    try:
        # Create new icon
        new_icon = TaskIcon(
            image_url=icon_data.image_url
        )
        
        db.add(new_icon)
        db.commit()
        db.refresh(new_icon)
        
        return TaskIconOut.from_orm(new_icon)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task icon: {str(e)}"
        )

def update_task_icon(db: Session, icon_id: int, icon_data: TaskIconUpdate) -> TaskIconOut:
    """Update an existing task icon"""
    try:
        # Get existing icon
        icon = db.execute(
            select(TaskIcon).where(TaskIcon.id == icon_id)
        ).scalars().first()
        
        if not icon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task icon not found"
            )
        
        # Update icon fields
        update_data = icon_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(icon, field, value)
        
        icon.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(icon)
        
        return TaskIconOut.from_orm(icon)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task icon: {str(e)}"
        )

def delete_task_icon(db: Session, icon_id: int) -> dict:
    """Delete a task icon"""
    try:
        icon = db.execute(
            select(TaskIcon).where(TaskIcon.id == icon_id)
        ).scalars().first()
        
        if not icon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task icon not found"
            )
        
        db.delete(icon)
        db.commit()
        
        return {
            "statusCode": 200,
            "status": True,
            "message": "Task icon deleted successfully",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task icon: {str(e)}"
        )

def seed_default_task_icons(db: Session) -> None:
    """Seed database with default kawaii flat style task icons"""
    try:
        # Check if icons already exist
        existing_icons = db.execute(select(TaskIcon)).scalars().all()
        if existing_icons:
            return  # Icons already seeded
        
        # Auto-discover icons from uploads directory
        import os
        from pathlib import Path
        
        uploads_dir = Path("uploads/task_icons")
        discovered_icons = []
        
        if uploads_dir.exists() and uploads_dir.is_dir():
            for entry in os.listdir(uploads_dir):
                entry_path = uploads_dir / entry
                if entry_path.is_file() and entry_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
                    # Store half URL for static serving
                    discovered_icons.append(f"/uploads/task_icons/{entry}")
        
        # Seed discovered icons
        for image_url in discovered_icons:
            db.add(TaskIcon(image_url=image_url))
        
        db.commit()
        logger.info(f"Seeded {len(discovered_icons)} default task icons")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed default task icons: {str(e)}")

