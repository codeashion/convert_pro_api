from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .service import (
    get_all_family_member_points,
    get_family_member_points_by_id,
    add_family_member_points,
    update_family_member_points,
    delete_family_member_points
)
from .model import FamilyMemberPointsCreate, FamilyMemberPointsOut

router = APIRouter(prefix="/family-member-points", tags=["family-member-points"])

@router.get("/", response_model=list[FamilyMemberPointsOut])
def get_all(token: str, db: Session = Depends(get_db)):
    return get_all_family_member_points(db, token)

@router.get("/{id}", response_model=FamilyMemberPointsOut)
def get_by_id(id: int, token: str, db: Session = Depends(get_db)):
    return get_family_member_points_by_id(db, token, id)

@router.post("/add", response_model=FamilyMemberPointsOut)
def add(token: str, data: FamilyMemberPointsCreate, db: Session = Depends(get_db)):
    return add_family_member_points(db, token, data)

@router.put("/{id}", response_model=FamilyMemberPointsOut)
def update(id: int, token: str, data: FamilyMemberPointsCreate, db: Session = Depends(get_db)):
    return update_family_member_points(db, token, id, data)

@router.delete("/{id}")
def delete(id: int, token: str, db: Session = Depends(get_db)):
    return delete_family_member_points(db, token, id)
