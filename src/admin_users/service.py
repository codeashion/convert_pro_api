import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from ..admin_users.models import User, FamilyMember, UserCreate, UserLogin, Admin
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_user(db: Session, user_data: UserCreate) -> Dict:
    try:
        existing = db.execute(select(User).where(User.email == user_data.email)).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = get_password_hash(user_data.password)
        new_user = User(full_name=user_data.full_name, email=user_data.email, password=hashed_pw)
        db.add(new_user)
        db.flush()  # To get new_user.id before commit

        for member in user_data.family_members:
            family = FamilyMember(
                user_id=new_user.id,
                member_name=member.member_name,
                date_of_birth=member.date_of_birth,
                assigned_colour=member.assigned_colour,
                image_path=member.image_path,
                voice_recording=member.voice_recording
            )
            db.add(family)

        db.commit()
        db.refresh(new_user)

        return {
            "statusCode": 200,
            "status": True,
            "message": "Parent registered successfully",
            "data": {
                "parent": {
                    "id": new_user.id,
                    "full_name": new_user.full_name,
                    "email": new_user.email,
                    "family_members": [
                        {
                            "id": f.id,
                            "member_name": f.member_name,
                            "date_of_birth": f.date_of_birth,
                            "assigned_colour": f.assigned_colour,
                            "image_path": f.image_path,
                            "voice_recording": f.voice_recording,
                        } for f in new_user.family_members
                    ]
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

def login_user(db: Session, user_data: UserLogin) -> Dict:
    """Login function for regular parents - searches parents table"""
    try:
        result = db.execute(select(User).where(User.email == user_data.email))
        user = result.scalars().first()

        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        token = create_access_token(
            data={"id": str(user.id), "email": user.email}
        )

        return {
            "statusCode": 200,
            "status": True,
            "message": "Login successful",
            "data": {
                "parent": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name
                },
                "access_token": token,
                "token_type": "bearer"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

def login_admin(db: Session, user_data: UserLogin) -> Dict:
    """Login function specifically for admin users - searches admin table"""
    try:
        result = db.execute(select(Admin).where(Admin.email == user_data.email))
        admin = result.scalars().first()

        if not admin or not verify_password(user_data.password, admin.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        token = create_access_token(
            data={"id": str(admin.id), "email": admin.email, "role": "admin"}
        )

        return {
            "statusCode": 200,
            "status": True,
            "message": "Admin login successful",
            "data": {
                "admin": {
                    "id": admin.id,
                    "email": admin.email,
                    "full_name": admin.full_name
                },
                "access_token": token,
                "token_type": "bearer"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Admin login failed: {str(e)}")

    # --- CRUD for admin user ---

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get parent user by ID"""
    return db.get(User, user_id)

def get_admin_by_id(db: Session, admin_id: int) -> Optional[Admin]:
    """Get admin user by ID"""
    return db.get(Admin, admin_id)

def update_user(db: Session, user_id: int, user_data: UserCreate) -> Optional[User]:
    """Update parent user"""
    user = db.get(User, user_id)
    if not user:
        return None
    user.full_name = user_data.full_name
    user.email = user_data.email
    user.password = get_password_hash(user_data.password)
    db.commit()
    db.refresh(user)
    return user

def update_admin(db: Session, admin_id: int, user_data: UserCreate) -> Optional[Admin]:
    """Update admin user"""
    admin = db.get(Admin, admin_id)
    if not admin:
        return None
    admin.full_name = user_data.full_name
    admin.email = user_data.email
    admin.password = get_password_hash(user_data.password)
    db.commit()
    db.refresh(admin)
    return admin

def delete_user(db: Session, user_id: int) -> bool:
    """Delete parent user"""
    user = db.get(User, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

def delete_admin(db: Session, admin_id: int) -> bool:
    """Delete admin user"""
    admin = db.get(Admin, admin_id)
    if not admin:
        return False
    db.delete(admin)
    db.commit()
    return True

# Alias for backward compatibility
hash_password = get_password_hash


def check_user_exists(db: Session, email: str) -> Dict:
    """
    Check if a user exists by email. If exists, return all user details (including password) in response format.
    If not exists, return null in data.
    """
    try:
        result = db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            token = create_access_token(
                data={"id": str(user.id), "email": user.email}
            )
            return {
                "statusCode": 200,
                "status": True,
                "message": "Login successful",
                "data": {
                    "parent": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "password": user.password,
                        "profile_image": user.profile_image,
                        "google_id": user.google_id,
                        "apple_id": user.apple_id,
                        "provider": user.provider,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    },
                    "access_token": token,
                    "token_type": "bearer"
                }
            }
        else:
            return {
                "statusCode": 200,
                "status": True,
                "message": "User not found",
                "data": None
            }
    except Exception as e:
        logger.error(f"Check user exists error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Check user exists failed: {str(e)}")


