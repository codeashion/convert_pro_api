from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..admin_users.service import create_user, login_user
from ..admin_users.models import UserCreate, UserLogin
from ..database import get_db

router = APIRouter(
    prefix="/adminusers",
    tags=["admin-users"]
)

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user)
