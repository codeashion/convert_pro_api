from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..completed_task.service import (
	get_all_completed_tasks,
	get_completed_task_by_id,
	add_completed_task,
	update_completed_task,
	delete_completed_task
)
from ..completed_task.model import CompletedTaskCreate, CompletedTaskOut

router = APIRouter(prefix="/completed-task", tags=["completed-task"])

@router.get("/", response_model=list[CompletedTaskOut])
def get_all(token: str, db: Session = Depends(get_db)):
	return get_all_completed_tasks(db, token)

@router.get("/{task_id}", response_model=CompletedTaskOut)
def get_by_id(task_id: int, token: str, db: Session = Depends(get_db)):
	return get_completed_task_by_id(db, token, task_id)

@router.post("/add", response_model=CompletedTaskOut)
def add(token: str, data: CompletedTaskCreate, db: Session = Depends(get_db)):
	# Ignore family_member_id from request, let service fetch it
	data_dict = data.dict(exclude={"family_member_id"})
	data = CompletedTaskCreate(**data_dict)
	return add_completed_task(db, token, data)

@router.put("/{task_id}", response_model=CompletedTaskOut)
def update(task_id: int, token: str, data: CompletedTaskCreate, db: Session = Depends(get_db)):
	# Ignore family_member_id from request, let service handle it
	data_dict = data.dict(exclude={"family_member_id"})
	data = CompletedTaskCreate(**data_dict)
	return update_completed_task(db, token, task_id, data)

@router.delete("/{task_id}")
def delete(task_id: int, token: str, db: Session = Depends(get_db)):
	return delete_completed_task(db, token, task_id)
