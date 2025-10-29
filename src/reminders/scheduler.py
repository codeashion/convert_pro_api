from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, date
from .models import Reminder

def auto_create_repeating_reminders(db: Session):
    now = datetime.now()
    today = now.date()
    current_time = now.time()

    # Query all reminders with repeat_pattern and is_active
    repeating_reminders = db.query(Reminder).filter(
        Reminder.repeat_pattern.in_(["Daily", "Weekly", "Monthly", "Yearly"]),
        Reminder.is_active == True
    ).all()

    for reminder in repeating_reminders:
        # Only create if not exists and time matches
        exists = db.query(Reminder).filter(
            Reminder.user_id == reminder.user_id,
            Reminder.title == reminder.title,
            Reminder.reminder_date == today,
            Reminder.reminder_time == reminder.reminder_time,
            Reminder.repeat_pattern == reminder.repeat_pattern
        ).first()
        if not exists and current_time.hour == reminder.reminder_time.hour and current_time.minute == reminder.reminder_time.minute:
            new_reminder = Reminder(
                user_id=reminder.user_id,
                title=reminder.title,
                reminder_date=today,
                reminder_time=reminder.reminder_time,
                repeat_pattern=reminder.repeat_pattern,
                family_member_id=reminder.family_member_id,
                voice_note=reminder.voice_note,
                message=reminder.message,
                audio_file=reminder.audio_file,
                is_active=True
            )
            db.add(new_reminder)
            db.commit()
            db.refresh(new_reminder)

def start_reminder_scheduler(db: Session):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: auto_create_repeating_reminders(db), 'interval', minutes=1)
    scheduler.start()
