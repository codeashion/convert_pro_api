from sqlalchemy.orm import Session
from datetime import date, timedelta
from sqlalchemy import func
from ..auth import verify_token
from ..admin_users.models import FamilyMember
from ..tasks.models import Task, TaskAssignment
from ..reminders.models import Reminder
from calendar import monthrange
from ..completed_task.model import CompletedTask

# Try common alternatives for the date field in TaskAssignment

# def get_calendar_tasks(db: Session, token: str) -> dict:
# 	"""
# 	Fetch all family members for the user (from token),
# 	and get their assigned tasks for today and next available date.
# 	"""
# 	token_data = verify_token(token)
# 	user_id = int(token_data.get("id"))

# 	today = date.today()

# 	# Get all family members for this user
# 	family_members = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).all()

# 	# Use 'assigned_at' as the date field
# 	date_field = "assigned_at"

# 	# Prepare result structure
# 	result = {"today": [], "next": [], "next_date": None}

# 	# For each family member, get today's tasks
# 	for member in family_members:
# 		assignments = db.query(TaskAssignment).filter(
# 			TaskAssignment.family_member_id == member.id
# 		).all()
# 		tasks_today = []
# 		for assign in assignments:
# 			task = db.query(Task).get(assign.task_id)
# 			if task and task.task_date == today:
# 				tasks_today.append({
# 					"task_id": task.id,
# 					"title": task.title,
# 					"date": task.task_date,
# 					"time": task.task_time,
# 					"points": task.points,
# 					"status": task.is_completed
# 				})
# 		result["today"].append({
# 			"family_member_id": member.id,
# 			"member_name": member.member_name,
# 			"assigned_colour": getattr(member, "assigned_colour", None),
# 			"image_path": getattr(member, "image_path", None),
# 			"member_type": getattr(member, "member_type", None),
# 			"tasks": tasks_today
# 		})

# 	# Find next available date with assignments for any member, up to end of month
# 	from calendar import monthrange
# 	next_date = None
# 	year = today.year
# 	month = today.month
# 	last_day = monthrange(year, month)[1]
# 	for offset in range(1, last_day - today.day + 1):
# 		check_date = today + timedelta(days=offset)
# 		has_data = db.query(TaskAssignment).filter(
# 			TaskAssignment.family_member_id.in_([m.id for m in family_members]),
# 		).all()
# 		found = False
# 		for assign in has_data:
# 			task = db.query(Task).get(assign.task_id)
# 			if task and task.task_date == check_date:
# 				next_date = check_date
# 				found = True
# 				break
# 		if found:
# 			break

# 	result["next_date"] = next_date
# 	if next_date:
# 		for member in family_members:
# 			assignments = db.query(TaskAssignment).filter(
# 				TaskAssignment.family_member_id == member.id
# 			).all()
# 			tasks_next = []
# 			for assign in assignments:
# 				task = db.query(Task).get(assign.task_id)
# 				if task and task.task_date == next_date:
# 					tasks_next.append({
# 						"task_id": task.id,
# 						"title": task.title,
# 						"date": task.task_date,
# 						"time": task.task_time,
# 						"points": task.points,
# 						"status": task.is_completed
# 					})
# 			result["next"].append({
# 				"family_member_id": member.id,
# 				"member_name": member.member_name,
# 				"assigned_colour": getattr(member, "assigned_colour", None),
# 				"image_path": getattr(member, "image_path", None),
# 				"member_type": getattr(member, "member_type", None),
# 				"tasks": tasks_next
# 			})

# 	return result



def get_calendar_tasks(db: Session, token: str) -> dict:
    """
    Fetch all family members for the user (from token),
    and get their assigned tasks for today and next available date.

    Tasks that have an entry in completed_task (CompletedTask.task_id)
    are treated as done and will NOT be returned.
    """
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))

    today = date.today()

    # Get family members for this user
    family_members = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).all()
    member_ids = [m.id for m in family_members]

    # Prepare result structure
    result = {"today": [], "next": [], "next_date": None}

    if not member_ids:
        return result

    # Prefetch all assignments for these family members
    assignments = db.query(TaskAssignment).filter(
        TaskAssignment.family_member_id.in_(member_ids)
    ).all()

    # Collect all assigned task_ids
    assigned_task_ids = list({a.task_id for a in assignments if a.task_id is not None})
    if not assigned_task_ids:
        # no assigned tasks at all
        # still return family member list with empty tasks
        for member in family_members:
            result["today"].append({
                "family_member_id": member.id,
                "member_name": member.member_name,
                "assigned_colour": getattr(member, "assigned_colour", None),
                "image_path": getattr(member, "image_path", None),
                "member_type": getattr(member, "member_type", None),
                "tasks": []
            })
        return result

    # Get task_ids that are completed (present in completed_task table)
    completed_rows = db.query(CompletedTask.task_id).filter(
        CompletedTask.task_id.in_(assigned_task_ids)
    ).all()
    # completed_rows is list of tuples, extract ids
    completed_task_ids = {row[0] for row in completed_rows if row[0] is not None}

    # Now fetch all assigned tasks (Task objects) for assigned_task_ids excluding completed ones
    pending_task_ids = [tid for tid in assigned_task_ids if tid not in completed_task_ids]
    if not pending_task_ids:
        # all assigned tasks are completed
        for member in family_members:
            result["today"].append({
                "family_member_id": member.id,
                "member_name": member.member_name,
                "assigned_colour": getattr(member, "assigned_colour", None),
                "image_path": getattr(member, "image_path", None),
                "member_type": getattr(member, "member_type", None),
                "tasks": []
            })
        return result

    tasks = db.query(Task).filter(Task.id.in_(pending_task_ids)).all()
    tasks_by_id = {t.id: t for t in tasks}

    # Build a mapping from family_member_id -> list of assignment.task_id
    assignments_by_member = {}
    for a in assignments:
        # only include assigned task ids that are still pending
        if a.task_id in pending_task_ids:
            assignments_by_member.setdefault(a.family_member_id, []).append(a.task_id)

    # Populate today's tasks grouped by family member
    for member in family_members:
        member_task_list = []
        for tid in assignments_by_member.get(member.id, []):
            task = tasks_by_id.get(tid)
            if not task:
                continue
            # Compare date field (your model used task.task_date previously)
            if getattr(task, "task_date", None) == today:
                member_task_list.append({
                    "task_id": task.id,
                    "title": task.title,
                    "date": task.task_date,
                    "time": getattr(task, "task_time", None),
                    "points": getattr(task, "points", None),
                    "status": getattr(task, "is_completed", None)
                })

        result["today"].append({
            "family_member_id": member.id,
            "member_name": member.member_name,
            "assigned_colour": getattr(member, "assigned_colour", None),
            "image_path": getattr(member, "image_path", None),
            "member_type": getattr(member, "member_type", None),
            "tasks": member_task_list
        })

    # Find next available date with pending (not completed) tasks for these members, up to end of month
    year = today.year
    month = today.month
    last_day = monthrange(year, month)[1]

    # Instead of querying in loop, fetch pending tasks with date > today and <= end of month
    # then pick the minimum date that has assignments
    pending_future_tasks = db.query(Task).filter(
        Task.id.in_(pending_task_ids),
        Task.task_date > today,
        Task.task_date <= date(year, month, last_day)
    ).all()

    if pending_future_tasks:
        # Group pending future tasks by date
        dates_with_tasks = {}
        for t in pending_future_tasks:
            dates_with_tasks.setdefault(t.task_date, []).append(t.id)

        # Find the earliest date
        next_date = min(dates_with_tasks.keys())
        result["next_date"] = next_date

        # Build tasks per member for that date
        for member in family_members:
            member_tasks_next = []
            for tid in assignments_by_member.get(member.id, []):
                task = tasks_by_id.get(tid)
                if not task:
                    # If task wasn't in tasks_by_id (maybe date > today), check from pending_future_tasks
                    # Build a small lookup
                    continue
                if getattr(task, "task_date", None) == next_date:
                    member_tasks_next.append({
                        "task_id": task.id,
                        "title": task.title,
                        "date": task.task_date,
                        "time": getattr(task, "task_time", None),
                        "points": getattr(task, "points", None),
                        "status": getattr(task, "is_completed", None)
                    })

            # It's possible some pending future tasks were not present in `tasks` fetched earlier (depending on id lists);
            # ensure we also include tasks from pending_future_tasks that match this member's assignments.
            # Build quick lookup of pending_future_tasks by id
            pending_future_by_id = {t.id: t for t in pending_future_tasks}
            # include tasks from pending_future_by_id if they belong to this member
            for tid in assignments_by_member.get(member.id, []):
                if tid in pending_future_by_id and (pending_future_by_id[tid].task_date == next_date):
                    # avoid duplicate
                    if not any(x["task_id"] == tid for x in member_tasks_next):
                        t = pending_future_by_id[tid]
                        member_tasks_next.append({
                            "task_id": t.id,
                            "title": t.title,
                            "date": t.task_date,
                            "time": getattr(t, "task_time", None),
                            "points": getattr(t, "points", None),
                            "status": getattr(t, "is_completed", None)
                        })

            result["next"].append({
                "family_member_id": member.id,
                "member_name": member.member_name,
                "assigned_colour": getattr(member, "assigned_colour", None),
                "image_path": getattr(member, "image_path", None),
                "member_type": getattr(member, "member_type", None),
                "tasks": member_tasks_next
            })

    return result


def get_month_tasks_reminders(db: Session, token: str, year: int, month: int) -> dict:
	"""
	Return date-wise full month tasks and reminders with family member details.
	"""
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	family_members = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).all()
	last_day = monthrange(year, month)[1]
	result = {}

	for day in range(1, last_day + 1):
		date_obj = date(year, month, day)
		day_data = {"tasks": [], "reminders": []}

		for member in family_members:
			assignments = db.query(TaskAssignment).filter(
				TaskAssignment.family_member_id == member.id
			).all()
			for assign in assignments:
				task = db.query(Task).get(assign.task_id)
				if task and task.task_date == date_obj:
					day_data["tasks"].append({
						"task_id": task.id,
						"title": task.title,
						"date": task.task_date,
						"time": task.task_time,
						"task_time": task.task_time,
						"points": task.points,
						"status": task.is_completed,
						"family_member_id": member.id,
						"member_name": member.member_name,
						"assigned_colour": getattr(member, "assigned_colour", None),
						"image_path": getattr(member, "image_path", None),
						"icon": getattr(task, "icon", None)
					})
		# Reminders for the day from Reminder model
		reminders = db.query(Reminder).filter(Reminder.reminder_date == date_obj).all()
		for reminder in reminders:
			day_data["reminders"].append({
				"id": reminder.id,
				"title": reminder.title,
				"reminder_date": reminder.reminder_date,
				"reminder_time": reminder.reminder_time,
				"repeat_pattern": getattr(reminder, "repeat_pattern", None),
				"family_member_id": reminder.family_member_id,
				"family_member_name": getattr(reminder, "family_member_name", None),
				"voice_note": getattr(reminder, "voice_note", None),
				"message": getattr(reminder, "message", None),
				"audio_file": getattr(reminder, "audio_file", None),
				"is_active": getattr(reminder, "is_active", None),
				"created_at": getattr(reminder, "created_at", None),
				"updated_at": getattr(reminder, "updated_at", None)
			})

		result[str(date_obj)] = day_data

	return result
