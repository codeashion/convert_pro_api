from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select
from ..admin_users.models import User, FamilyMember, FamilyMemberCreate
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
