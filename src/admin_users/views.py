
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..admin_users.service import create_user, login_admin, get_admin_by_id, update_admin, delete_admin, check_user_exists
from ..admin_users.models import UserCreate, UserLogin, UserOut
from ..database import get_db
from pydantic import BaseModel

class EmailRequest(BaseModel):
    email: str

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_admin(db, user)

# Only GET and UPDATE endpoints for admin
@router.get("/getadmin", response_model=UserOut)
def get_admin(db: Session = Depends(get_db)):
    # Always return the first admin (id=1)
    admin = get_admin_by_id(db, 1)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    # Convert Admin to UserOut format
    return {
        "id": admin.id,
        "full_name": admin.full_name,
        "email": admin.email,
        "family_members": []  # Admins don't have family members
    }

@router.put("/updateadmin", response_model=UserOut)
def update_admin_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    updated = update_admin(db, 1, user)
    if not updated:
        raise HTTPException(status_code=404, detail="Admin not found")
    # Convert Admin to UserOut format
    return {
        "id": updated.id,
        "full_name": updated.full_name,
        "email": updated.email,
        "family_members": []  # Admins don't have family members
    }

@router.post("/check-user-exists")
def check_user_exists_api(request: EmailRequest, db: Session = Depends(get_db)):
    return check_user_exists(db, request.email)
