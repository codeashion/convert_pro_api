from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select
from ..completed_task.model import CompletedTask, CompletedTaskCreate, CompletedTaskOut
from ..auth import verify_token


# Import TaskAssignment from tasks.models
from ..tasks.models import TaskAssignment

def get_all_completed_tasks(db: Session, token: str):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	return db.execute(select(CompletedTask).where(CompletedTask.user_id == user_id)).scalars().all()

def get_completed_task_by_id(db: Session, token: str, task_id: int):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	task = db.get(CompletedTask, task_id)
	if not task or task.user_id != user_id:
		raise HTTPException(status_code=404, detail="Completed task not found")
	return task

def add_completed_task(db: Session, token: str, data: CompletedTaskCreate):
	token_data = verify_token(token)
	user_id = int(token_data.get("id")) 
	# Fetch family_member_id from task_assignment table using task_id
	from sqlalchemy import select
	assignment = db.execute(
		select(TaskAssignment.family_member_id).where(TaskAssignment.task_id == data.task_id)
	).first() 
	family_member_id = assignment[0] if assignment else None
	new_task = CompletedTask(user_id=user_id, family_member_id=family_member_id, **data.dict(exclude={"family_member_id"}))
	db.add(new_task)
	db.commit()
	db.refresh(new_task)

	# Call add_family_member_points after successful add
	from ..family_member_points.service import add_family_member_points
	from ..family_member_points.model import FamilyMemberPointsCreate
	points_data = FamilyMemberPointsCreate(
		family_member_id=family_member_id,
		total_points=data.point if hasattr(data, 'point') else 0
	)
	add_family_member_points(db, token, points_data)

	return new_task

def update_completed_task(db: Session, token: str, task_id: int, data: CompletedTaskCreate):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	task = db.get(CompletedTask, task_id)
	if not task or task.user_id != user_id:
		raise HTTPException(status_code=404, detail="Completed task not found")
	for key, value in data.dict().items():
		setattr(task, key, value)
	db.commit()
	db.refresh(task)
	return task

def delete_completed_task(db: Session, token: str, task_id: int):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	task = db.get(CompletedTask, task_id)
	if not task or task.user_id != user_id:
		raise HTTPException(status_code=404, detail="Completed task not found")
	db.delete(task)
	db.commit()
	return {"status": True, "message": "Completed task deleted"}
