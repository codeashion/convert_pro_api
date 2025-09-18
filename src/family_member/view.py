from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..database import get_db

from ..family_member.service import (
    get_all_family_members,
    get_family_member_by_id,
    add_family_member,
    update_family_member,
    delete_family_member,
    get_leaderboard_service
)
from ..admin_users.models import FamilyMemberCreate, FamilyMemberOut, LeaderboardMemberOut

router = APIRouter(prefix="/family-members", tags=["family-members"])

@router.get("/", response_model=list[FamilyMemberOut])
def get_all(db: Session = Depends(get_db), token: str = Header(...)):
    return get_all_family_members(db, token)

@router.get("/leaderboard")
def get_leaderboard_endpoint(
    db: Session = Depends(get_db),
    token: str = Header(..., alias="token")
):
    """
    Get leaderboard: member_name, assigned_colour, total_points
    """
    return get_leaderboard_service(db, token)

@router.get("/today-task-leaderboard")
def get_today_task_leaderboard_endpoint(
    db: Session = Depends(get_db),
    token: str = Header(..., alias="token")
):
    """
    Get today's task leaderboard: member_name, assigned_colour, image_path, total_tasks, completed_tasks, points
    """
    from ..family_member.service import get_today_task_leaderboard
    return get_today_task_leaderboard(db, token)


@router.get("/{family_member_id}", response_model=FamilyMemberOut)
def get_by_id(family_member_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    return get_family_member_by_id(db, family_member_id, token)

@router.post("/add", response_model=FamilyMemberOut)
def add(member_data: FamilyMemberCreate, db: Session = Depends(get_db), token: str = Header(...)):
    return add_family_member(db, token, member_data)

@router.put("/{family_member_id}", response_model=FamilyMemberOut)
def update(family_member_id: int, updated_data: FamilyMemberCreate, db: Session = Depends(get_db), token: str = Header(...)):
    return update_family_member(db, family_member_id, updated_data, token)

@router.delete("/{family_member_id}")
def delete(family_member_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    return delete_family_member(db, family_member_id, token)
