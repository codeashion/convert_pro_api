from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..family_member.service import (
    get_all_family_members,
    get_family_member_by_id,
    add_family_member,
    update_family_member,
    delete_family_member
)
from ..admin_users.models import FamilyMemberCreate, FamilyMemberOut

router = APIRouter(prefix="/family-members", tags=["family-members"])


@router.get("/", response_model=list[FamilyMemberOut])
def get_all(db: Session = Depends(get_db), token: str = Header(...)):
    return get_all_family_members(db, token)


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
