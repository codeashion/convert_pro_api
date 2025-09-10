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
from ..auth import verify_token

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

def create_user(db: Session, user_data: UserCreate, role: str = "parent") -> Dict:
    """Create a new user (parent only - admins are created separately)"""
    try:
        # Check if email already exists in both tables
        existing_user = db.execute(select(User).where(User.email == user_data.email)).scalars().first()
        existing_admin = db.execute(select(Admin).where(Admin.email == user_data.email)).scalars().first()

        if existing_user or existing_admin:
            logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=400,
                detail=f"An account with email '{user_data.email}' already exists. Please use a different email or try logging in."
            )

        # Validate password confirmation
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="Password and confirm password do not match. Please ensure both passwords are identical."
            )

        hashed_pw = get_password_hash(user_data.password)
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password=hashed_pw,
            provider="email"  # Set provider for email-based signups
        )
        db.add(new_user)
        db.flush()  # To get new_user.id before commit

        # Create family members if provided
        family_members_created = []
        for member in user_data.family_members:
            try:
                family = FamilyMember(
                    user_id=new_user.id,
                    member_name=member.member_name,
                    date_of_birth=member.date_of_birth,
                    assigned_colour=member.assigned_colour,
                    image_path=member.image_path,
                    voice_recording=member.voice_recording
                )
                db.add(family)
                family_members_created.append(family)
            except Exception as e:
                logger.error(f"Error creating family member {member.member_name}: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Error creating family member '{member.member_name}': {str(e)}"
                )

        db.commit()
        db.refresh(new_user)

        # Create JWT token for the new user
        access_token = create_access_token({"id": str(new_user.id), "email": new_user.email, "role": "parent"})

        logger.info(f"Successfully created user: {new_user.email} with {len(family_members_created)} family members")

        return {
            "statusCode": 200,
            "status": True,
            "message": f"User '{user_data.full_name}' registered successfully with {len(family_members_created)} family members",
            "data": {
                "parent": {
                    "id": new_user.id,
                    "full_name": new_user.full_name,
                    "email": new_user.email,
                    "role": "parent",
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
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during user signup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed due to a server error. Please try again later or contact support if the issue persists."
        )

def login_user(db: Session, user_data: UserLogin) -> Dict:
    """Universal login for parents and admins"""
    try:
        # Validate input
        if not user_data.email or not user_data.email.strip():
            raise HTTPException(
                status_code=400,
                detail="Email address is required. Please provide a valid email."
            )

        if not user_data.password or not user_data.password.strip():
            raise HTTPException(
                status_code=400,
                detail="Password is required. Please provide your password."
            )

        # First try to find in admin table
        admin_result = db.execute(select(Admin).where(Admin.email == user_data.email.strip().lower()))
        admin = admin_result.scalars().first()

        if admin and verify_password(user_data.password, admin.password):
            token = create_access_token(
                data={"id": str(admin.id), "email": admin.email, "role": "admin"}
            )
            logger.info(f"Successful admin login: {admin.email}")
            return {
                "statusCode": 200,
                "status": True,
                "message": f"Welcome back, {admin.full_name}! Admin login successful.",
                "data": {
                    "admin": {
                        "id": admin.id,
                        "email": admin.email,
                        "full_name": admin.full_name,
                        "role": "admin"
                    },
                    "access_token": token,
                    "token_type": "bearer"
                }
            }

        # Then try to find in parents table
        user_result = db.execute(select(User).where(User.email == user_data.email.strip().lower()))
        user = user_result.scalars().first()

        if user and verify_password(user_data.password, user.password):
            token = create_access_token(
                data={"id": str(user.id), "email": user.email, "role": "parent"}
            )
            logger.info(f"Successful parent login: {user.email}")
            return {
                "statusCode": 200,
                "status": True,
                "message": f"Welcome back, {user.full_name}! Login successful.",
                "data": {
                    "parent": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": "parent"
                    },
                    "access_token": token,
                    "token_type": "bearer"
                }
            }

        # No valid user found
        logger.warning(f"Failed parent/admin login attempt for email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials and try again. If you don't have a parent account, please sign up first."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Login service temporarily unavailable. Please try again later."
        )

def get_user_profile(db: Session, token: str) -> Dict:
    """Get current user profile"""
    payload = verify_token(token)
    user_id = int(payload["id"])
    user_role = payload.get("role", "parent")

    if user_role == "admin":
        admin = db.get(Admin, user_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return {
            "id": admin.id,
            "full_name": admin.full_name,
            "email": admin.email,
            "family_members": []  # Admins don't have family members
        }
    else:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Parent not found")
        return user

def update_user_profile(db: Session, token: str, user_data: UserCreate) -> Dict:
    """Update current user profile"""
    payload = verify_token(token)
    user_id = int(payload["id"])
    user_role = payload.get("role", "parent")

    if user_role == "admin":
        admin = db.get(Admin, user_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        if user_data.full_name is not None:
            admin.full_name = user_data.full_name
        if user_data.email is not None:
            admin.email = user_data.email
        if user_data.password is not None:
            admin.password = get_password_hash(user_data.password)
        db.commit()
        db.refresh(admin)
        return {
            "id": admin.id,
            "full_name": admin.full_name,
            "email": admin.email,
            "family_members": []
        }
    else:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Parent not found")
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.password is not None:
            user.password = get_password_hash(user_data.password)
        if user_data.profile_image is not None:
            user.profile_image = user_data.profile_image
        db.commit()
        db.refresh(user)
        return user

def delete_user_profile(db: Session, token: str) -> Dict:
    """Delete current user profile"""
    payload = verify_token(token)
    user_id = int(payload["id"])
    user_role = payload.get("role", "parent")

    if user_role == "admin":
        admin = db.get(Admin, user_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        db.delete(admin)
        db.commit()
        return {
            "statusCode": 200,
            "status": True,
            "message": "Admin deleted successfully",
            "data": None
        }
    else:
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Parent not found")
        db.delete(user)
        db.commit()
        return {
            "statusCode": 200,
            "status": True,
            "message": "Parent deleted successfully",
            "data": None
        }

# ======== ADMIN-ONLY FUNCTIONS ========

def require_admin(token: str) -> Dict:
    """Verify token and ensure user is admin with detailed error messages"""
    payload = verify_token(token)
    user_role = payload.get("role")

    if user_role != "admin":
        user_email = payload.get("email", "Unknown")
        logger.warning(f"Unauthorized admin access attempt by user: {user_email} with role: {user_role}")
        raise HTTPException(
            status_code=403,
            detail="Administrator privileges required. This action can only be performed by admin users. Please contact your administrator for access."
        )
    return payload

def get_all_users(db: Session, token: str) -> list:
    """Get all parents (admin only)"""
    require_admin(token)

    result = db.execute(select(User))
    users = result.scalars().all()
    return users

def get_user_by_id(db: Session, token: str, user_id: int) -> Dict:
    """Get parent by ID (admin only)"""
    require_admin(token)

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Parent not found")
    return user

def update_user_by_id(db: Session, token: str, user_id: int, user_data: UserCreate) -> Dict:
    """Update parent by ID (admin only)"""
    require_admin(token)

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Parent not found")

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.password = get_password_hash(user_data.password)
    db.commit()
    db.refresh(user)
    return user

def delete_user_by_id(db: Session, token: str, user_id: int) -> Dict:
    """Delete parent by ID (admin only)"""
    require_admin(token)

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Parent not found")

    db.delete(user)
    db.commit()
    return {
        "statusCode": 200,
        "status": True,
        "message": "Parent deleted successfully",
        "data": None
    }
