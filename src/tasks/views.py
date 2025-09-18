from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..tasks.service import (
    get_all_tasks, get_task_by_id, create_task, update_task, 
    delete_task, get_all_task_icons, get_task_icon_by_id, 
    create_task_icon, update_task_icon, delete_task_icon
)
from ..tasks.models import TaskCreate, TaskUpdate, TaskOut, TaskIconCreate, TaskIconUpdate, TaskIconOut
from ..database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskOut])
def get_tasks_endpoint(
    date: str,  # Required date in YYYY-MM-DD
    family_member_id: Optional[int] = None,  # Optional filter by assigned family member
    db: Session = Depends(get_db),
    token: str = Header(...)
):
    """Get all tasks filtered by date (required) and family member (optional)"""
    return get_all_tasks(db, token, date, family_member_id)

@router.get("/{task_id}", response_model=TaskOut)
def get_task_endpoint(
    task_id: int, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Get a specific task by ID"""
    return get_task_by_id(db, token, task_id)

@router.post("/add", response_model=TaskOut)
def create_task_endpoint(
    task_data: TaskCreate, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Create a new task"""
    return create_task(db, token, task_data)

@router.put("/{task_id}", response_model=TaskOut)
def update_task_endpoint(
    task_id: int, 
    task_data: TaskUpdate, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Update an existing task"""
    return update_task(db, token, task_id, task_data)

@router.delete("/{task_id}")
def delete_task_endpoint(
    task_id: int, 
    db: Session = Depends(get_db), 
    token: str = Header(...)
):
    """Delete a task"""
    return delete_task(db, token, task_id)



# Task Icons CRUD Endpoints

@router.get("/icons/", response_model=List[TaskIconOut])
def get_task_icons_endpoint(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all task icons"""
    return get_all_task_icons(db, limit, offset)

@router.get("/icons/{icon_id}", response_model=TaskIconOut)
def get_task_icon_endpoint(
    icon_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific task icon by ID"""
    return get_task_icon_by_id(db, icon_id)

@router.post("/icons/add", response_model=TaskIconOut)
def create_task_icon_endpoint(
    icon_data: TaskIconCreate,
    db: Session = Depends(get_db)
):
    """Create a new task icon"""
    return create_task_icon(db, icon_data)

@router.put("/icons/{icon_id}", response_model=TaskIconOut)
def update_task_icon_endpoint(
    icon_id: int,
    icon_data: TaskIconUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing task icon"""
    return update_task_icon(db, icon_id, icon_data)

@router.delete("/icons/{icon_id}")
def delete_task_icon_endpoint(
    icon_id: int,
    db: Session = Depends(get_db)
):
    """Delete a task icon"""
    return delete_task_icon(db, icon_id)