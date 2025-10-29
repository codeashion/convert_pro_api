from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, date
from .models import Task, TaskAssignment
from ..reminders.models import Reminder

def auto_create_repeating_tasks(db: Session):
    now = datetime.now()
    today = now.date()
    current_time = now.time()

    # Query all tasks with repeat_pattern and reminder_enabled
    repeating_tasks = db.query(Task).filter(
        Task.repeat_pattern.in_(["Daily", "Weekly", "Monthly", "Yearly"]),
        Task.reminder_enabled == True
    ).all()

    for task in repeating_tasks:
        # Only create if not exists and time matches
        exists = db.query(Task).filter(
            Task.user_id == task.user_id,
            Task.title == task.title,
            Task.task_date == today,
            Task.task_time == task.task_time,
            Task.repeat_pattern == task.repeat_pattern
        ).first()
        if not exists and current_time.hour == task.task_time.hour and current_time.minute == task.task_time.minute:
            new_task = Task(
                user_id=task.user_id,
                title=task.title,
                task_date=today,
                task_time=task.task_time,
                repeat_pattern=task.repeat_pattern,
                points=task.points,
                icon=task.icon,
                is_private=task.is_private,
                reminder_enabled=task.reminder_enabled,
                voice_note=task.voice_note,
                tone=task.tone,
                message=task.message,
                audio_file=task.audio_file
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            # Copy assignments
            assignments = db.query(TaskAssignment).filter(TaskAssignment.task_id == task.id).all()
            for assignment in assignments:
                new_assignment = TaskAssignment(
                    task_id=new_task.id,
                    family_member_id=assignment.family_member_id
                )
                db.add(new_assignment)
            db.commit()
            # Copy reminder
            if task.reminder_enabled:
                reminder = Reminder(
                    user_id=task.user_id,
                    title=task.title,
                    reminder_date=today,
                    reminder_time=task.task_time,
                    repeat_pattern=task.repeat_pattern,
                    family_member_id=assignments[0].family_member_id if assignments else None,
                    message=task.message,
                    voice_note=task.voice_note,
                    audio_file=task.audio_file,
                    is_active=True
                )
                db.add(reminder)
                db.commit()
                db.refresh(reminder)

def start_scheduler(db: Session):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: auto_create_repeating_tasks(db), 'interval', minutes=1)
    scheduler.start()
