from ..completed_task.model import CompletedTask
from ..tasks.models import TaskAssignment
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select
from ..admin_users.models import User, FamilyMember, FamilyMemberCreate 
from ..family_member_points.model import FamilyMemberPoints 
from ..auth import verify_token 

def get_all_family_members(db: Session, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    print("Decoded User ID:", user_id)

    members = db.execute(
        select(FamilyMember).where(FamilyMember.user_id == user_id)
    ).scalars().all()

    print("Fetched Members:", members)
    return members

def get_family_member_by_id(db: Session, family_member_id: int, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    print("Decoded User ID:", user_id)

    member = db.get(FamilyMember, family_member_id)
    if not member or member.user_id != user_id:
        raise HTTPException(status_code=404, detail="Family member not found or unauthorized")
    return member

def add_family_member(db: Session, token: str, member_data: FamilyMemberCreate):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    print("Decoded User ID:", user_id)

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_member = FamilyMember(
        user_id=user_id,
        member_name=member_data.member_name,
        date_of_birth=member_data.date_of_birth,
        assigned_colour=member_data.assigned_colour,
        image_path=member_data.image_path,
        voice_recording=member_data.voice_recording
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    print("Added Member:", new_member)
    return new_member

def update_family_member(db: Session, family_member_id: int, updated_data: FamilyMemberCreate, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    print("Decoded User ID:", user_id)

    member = db.get(FamilyMember, family_member_id)
    if not member or member.user_id != user_id:
        raise HTTPException(status_code=404, detail="Family member not found or unauthorized")

    for field, value in updated_data.dict().items():
        if value is not None:
            setattr(member, field, value)

    db.commit()
    db.refresh(member)
    print("Updated Member:", member)
    return member

def delete_family_member(db: Session, family_member_id: int, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    print("Decoded User ID:", user_id)

    member = db.get(FamilyMember, family_member_id)
    if not member or member.user_id != user_id:
        raise HTTPException(status_code=404, detail="Family member not found or unauthorized")

    db.delete(member)
    db.commit()
    print(f"Deleted Member ID: {family_member_id}")
    return {"status": True, "message": "Family member deleted successfully"}

def get_leaderboard_service(db: Session, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))

    # Get all family members for the user
    members = db.execute(
        select(FamilyMember).where(FamilyMember.user_id == user_id)
    ).scalars().all()

    leaderboard = []
    for member in members:
        points_entry = db.query(FamilyMemberPoints).filter(
            FamilyMemberPoints.user_id == user_id,
            FamilyMemberPoints.family_member_id == member.id
        ).first()
        total_points = int(points_entry.total_points) if points_entry else 0
        leaderboard.append({
            "member_name": member.member_name,
            "assigned_colour": member.assigned_colour,
            "image_path": member.image_path,
            "total_points": total_points
        })

    # Sort by total_points descending
    leaderboard.sort(key=lambda x: x["total_points"], reverse=True)
    return leaderboard

def get_today_task_leaderboard(db: Session, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    today = date.today()

    members = db.execute(
        select(FamilyMember).where(FamilyMember.user_id == user_id)
    ).scalars().all()

    leaderboard = []
    for member in members:
        # Total tasks assigned today from task_assignment
        total_tasks = db.query(TaskAssignment).filter(
            TaskAssignment.family_member_id == member.id,
            TaskAssignment.assigned_at >= today,
            TaskAssignment.assigned_at < today.replace(day=today.day+1) if today.day < 28 else TaskAssignment.assigned_at <= today
        ).count()

        # Completed tasks today
        completed_tasks = db.query(CompletedTask).filter(
            CompletedTask.family_member_id == member.id,
            CompletedTask.created_at >= today,
            CompletedTask.created_at < today.replace(day=today.day+1) if today.day < 28 else CompletedTask.created_at <= today
        ).count()

        # Today's earned points
        today_points = db.query(CompletedTask).filter(
            CompletedTask.family_member_id == member.id,
            CompletedTask.created_at >= today,
            CompletedTask.created_at < today.replace(day=today.day+1) if today.day < 28 else CompletedTask.created_at <= today
        ).with_entities(CompletedTask.point).all()
        total_points = sum([p[0] for p in today_points]) if today_points else 0

        leaderboard.append({
            "member_name": member.member_name,
            "assigned_colour": member.assigned_colour,
            "image_path": member.image_path,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "points": total_points
        })

    return leaderboard
