from sqlalchemy.orm import Session
from fastapi import HTTPException
from .model import FamilyMemberPoints, FamilyMemberPointsCreate
from ..auth import verify_token

def get_all_family_member_points(db: Session, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    return db.query(FamilyMemberPoints).filter(FamilyMemberPoints.user_id == user_id).all()

def get_family_member_points_by_id(db: Session, token: str, id: int):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    points = db.get(FamilyMemberPoints, id)
    if not points or points.user_id != user_id:
        raise HTTPException(status_code=404, detail="Points record not found")
    return points

def add_family_member_points(db: Session, token: str, data: FamilyMemberPointsCreate):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    # Check if entry exists
    existing = db.query(FamilyMemberPoints).filter(
        FamilyMemberPoints.user_id == user_id,
        FamilyMemberPoints.family_member_id == data.family_member_id
    ).first()
    if existing:
        # Add new points to existing total_points
        existing.total_points += data.total_points
        db.commit()
        db.refresh(existing) 
        return existing
    else:
        new_points = FamilyMemberPoints(user_id=user_id, **data.dict())
        db.add(new_points)
        db.commit()
        db.refresh(new_points)
        return new_points

def update_family_member_points(db: Session, token: str, id: int, data: FamilyMemberPointsCreate):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    points = db.get(FamilyMemberPoints, id)
    if not points or points.user_id != user_id:
        raise HTTPException(status_code=404, detail="Points record not found")
    for key, value in data.dict().items():
        setattr(points, key, value)
    db.commit()
    db.refresh(points)
    return points

def delete_family_member_points(db: Session, token: str, id: int):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    points = db.get(FamilyMemberPoints, id)
    if not points or points.user_id != user_id:
        raise HTTPException(status_code=404, detail="Points record not found")
    db.delete(points)
    db.commit()
    return {"status": True, "message": "Points record deleted"}
