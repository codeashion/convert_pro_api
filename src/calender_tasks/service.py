from sqlalchemy.orm import Session
from datetime import date, timedelta
from sqlalchemy import func
from ..auth import verify_token
from ..admin_users.models import FamilyMember
from ..tasks.models import Task, TaskAssignment


# Try common alternatives for the date field in TaskAssignment
def get_calendar_tasks(db: Session, token: str) -> dict:
	"""
	Fetch all family members for the user (from token),
	and get their assigned tasks for today and next available date.
	"""
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))

	today = date.today()

	# Get all family members for this user
	family_members = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).all()

	# Use 'assigned_at' as the date field
	date_field = "assigned_at"

	# Prepare result structure
	result = {"today": [], "next": [], "next_date": None}

	# For each family member, get today's tasks
	for member in family_members:
		assignments = db.query(TaskAssignment).filter(
			TaskAssignment.family_member_id == member.id
		).all()
		tasks_today = []
		for assign in assignments:
			task = db.query(Task).get(assign.task_id)
			if task and task.task_date == today:
				tasks_today.append({
					"task_id": task.id,
					"title": task.title,
					"date": task.task_date,
					"time": task.task_time,
					"points": task.points,
					"status": task.is_completed
				})
		result["today"].append({
			"family_member_id": member.id,
			"member_name": member.member_name,
			"assigned_colour": getattr(member, "assigned_colour", None),
			"tasks": tasks_today
		})

	# Find next available date with assignments for any member, up to end of month
	from calendar import monthrange
	next_date = None
	year = today.year
	month = today.month
	last_day = monthrange(year, month)[1]
	for offset in range(1, last_day - today.day + 1):
		check_date = today + timedelta(days=offset)
		has_data = db.query(TaskAssignment).filter(
			TaskAssignment.family_member_id.in_([m.id for m in family_members]),
		).all()
		found = False
		for assign in has_data:
			task = db.query(Task).get(assign.task_id)
			if task and task.task_date == check_date:
				next_date = check_date
				found = True
				break
		if found:
			break

	result["next_date"] = next_date
	if next_date:
		for member in family_members:
			assignments = db.query(TaskAssignment).filter(
				TaskAssignment.family_member_id == member.id
			).all()
			tasks_next = []
			for assign in assignments:
				task = db.query(Task).get(assign.task_id)
				if task and task.task_date == next_date:
					tasks_next.append({
						"task_id": task.id,
						"title": task.title,
						"date": task.task_date,
						"time": task.task_time,
						"points": task.points,
						"status": task.is_completed
					})
			result["next"].append({
				"family_member_id": member.id,
				"member_name": member.member_name,
				"assigned_colour": getattr(member, "assigned_colour", None),
				"tasks": tasks_next
			})

	return result
