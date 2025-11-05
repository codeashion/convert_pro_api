
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
from ..home_essential.model import HomeEssential, Grocery
from ..rewards.models import Reward

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



# def create_user(db: Session, user_data: UserCreate, role: str = "parent") -> Dict:
#     """Create a new user (parent only - admins are created separately)"""
#     try:
#         # Check existing user
#         existing_user = db.execute(select(User).where(User.email == user_data.email)).scalars().first()
#         existing_admin = db.execute(select(Admin).where(Admin.email == user_data.email)).scalars().first()
#         if existing_user or existing_admin:
#             raise HTTPException(status_code=400, detail=f"Email '{user_data.email}' already exists.")

#         # Validate password match
#         if user_data.password != user_data.confirm_password:
#             raise HTTPException(status_code=400, detail="Passwords do not match.")

#         # Create new user
#         hashed_pw = get_password_hash(user_data.password)
#         new_user = User(full_name=user_data.full_name, email=user_data.email, password=hashed_pw, provider="email")
#         db.add(new_user)
#         db.flush()  # to get user_id before commit

#         # Add family members
#         for member in user_data.family_members:
#             family = FamilyMember(
#                 user_id=new_user.id,
#                 member_name=member.member_name,
#                 date_of_birth=member.date_of_birth,
#                 assigned_colour=member.assigned_colour,
#                 image_path=member.image_path,
#                 voice_recording=member.voice_recording,
#             )
#             db.add(family)

#         # ✅ Add default Home Essentials
#         home_essentials = [
#             "Toilet Paper",
#             "Laundry Detergent",
#             "Dishwashing Liquid",
#             "Garbage Bags",
#             "Cleaning Spray",
#             "Light Bulbs",
#             "Hand Soap",
#             "Paper Towels",
#             "Air Freshener",
#             "Batteries (AA/AAA)"
#         ]

#         for name in home_essentials:
#             db.add(HomeEssential(name=name, user_id=new_user.id, status=False))

#         # ✅ Add default Groceries
#         groceries = [
#             "Rice",
#             "Cooking Oil (Sunflower, Mustard, or Olive)",
#             "Salt, Sugar, and Spices",
#             "Milk",
#             "Bread",
#             "Vegetables (Onion, Potato, Tomato, etc.)",
#             "Fruits (Banana, Apple, Orange)",
#             "Tea",
#             "Pulses",
#             "Snacks"
#         ]

#         for name in groceries:
#             db.add(Grocery(name=name, user_id=new_user.id, status=False))

#         db.commit()
#         db.refresh(new_user)

#         # Create JWT token
#         access_token = create_access_token({"id": str(new_user.id), "email": new_user.email, "role": "parent"})

#         return {
#             "statusCode": 200,
#             "status": True,
#             "message": f"User '{user_data.full_name}' registered successfully. Default items added.",
#             "data": {
#                 "parent": {
#                     "id": new_user.id,
#                     "full_name": new_user.full_name,
#                     "email": new_user.email,
#                     "role": "parent",
#                 },
#                 "access_token": access_token,
#                 "token_type": "bearer"
#             }
#         }

#     except HTTPException:
#         db.rollback()
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Signup error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Registration failed due to a server error.")


def create_user(db: Session, user_data: UserCreate, role: str = "parent") -> Dict:
    """Create a new user (parent only - admins are created separately)"""
    try:
        # 🔹 Check existing user or admin
        existing_user = db.execute(select(User).where(User.email == user_data.email)).scalars().first()
        existing_admin = db.execute(select(Admin).where(Admin.email == user_data.email)).scalars().first()
        if existing_user or existing_admin:
            raise HTTPException(status_code=400, detail=f"Email '{user_data.email}' already exists.")

        # 🔹 Validate password match
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match.")

        # 🔹 Create new user
        hashed_pw = get_password_hash(user_data.password)
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password=hashed_pw,
            provider="email"
        )
        db.add(new_user)
        db.flush()  # Get user_id before commit

        # 🔹 Add family members
        for member in user_data.family_members:
            family = FamilyMember(
                user_id=new_user.id,
                member_name=member.member_name,
                date_of_birth=member.date_of_birth,
                assigned_colour=member.assigned_colour,
                image_path=member.image_path,
                voice_recording=member.voice_recording,
            )
            db.add(family)

        # ✅ Add default Home Essentials
        home_essentials = [
            "Toilet Paper",
            "Laundry Detergent",
            "Dishwashing Liquid",
            "Garbage Bags",
            "Cleaning Spray",
            "Light Bulbs",
            "Hand Soap",
            "Paper Towels",
            "Air Freshener",
            "Batteries (AA/AAA)"
        ]
        for name in home_essentials:
            db.add(HomeEssential(name=name, user_id=new_user.id, status=False))

        # ✅ Add default Groceries
        groceries = [
            "Rice",
            "Cooking Oil (Sunflower, Mustard, or Olive)",
            "Salt, Sugar, and Spices",
            "Milk",
            "Bread",
            "Vegetables (Onion, Potato, Tomato, etc.)",
            "Fruits (Banana, Apple, Orange)",
            "Tea",
            "Pulses",
            "Snacks"
        ]
        for name in groceries:
            db.add(Grocery(name=name, user_id=new_user.id, status=False))

        # ✅ Add default Rewards
        rewards = [
            "Star Performer",
            "Employee of the Month",
            "Outstanding Contributor",
            "Excellence Award",
            "Achiever’s Trophy",
            "Dedication Award",
            "Performance Champion",
            "Leadership Excellence",
            "Rising Star",
            "Hall of Fame"
        ]
        for reward_name in rewards:
            db.add(Reward(
                user_id=new_user.id,
                reward=reward_name,
                points="0",                # default point
                requested_by=None,
                created_by="System"         # optional for tracking
            ))

        # 🔹 Commit all inserts
        db.commit()
        db.refresh(new_user)

        # 🔹 Create JWT token
        access_token = create_access_token({
            "id": str(new_user.id),
            "email": new_user.email,
            "role": "parent"
        })

        return {
            "statusCode": 200,
            "status": True,
            "message": f"User '{user_data.full_name}' registered successfully. Default items added.",
            "data": {
                "parent": {
                    "id": new_user.id,
                    "full_name": new_user.full_name,
                    "email": new_user.email,
                    "role": "parent",
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
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed due to a server error.")


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

# ======== PASSWORD RESET FUNCTION ========
def reset_password(db: Session, token: str, current_password: str, new_password: str, confirm_new_password: str) -> Dict:
    """
    Reset password for current user (parent or admin).
    Checks current password, validates new password, updates if valid.
    """
    payload = verify_token(token)
    user_id = int(payload["id"])
    user_role = payload.get("role", "parent")

    if new_password != confirm_new_password:
        return {
            "statusCode": 400,
            "status": False,
            "message": "New password and confirm password do not match.",
            "data": None
        }

    if user_role == "admin":
        user = db.get(Admin, user_id)
    else:
        user = db.get(User, user_id)

    if not user:
        return {
            "statusCode": 404,
            "status": False,
            "message": "User not found.",
            "data": None
        }

    if not verify_password(current_password, user.password):
        return {
            "statusCode": 401,
            "status": False,
            "message": "Current password is incorrect.",
            "data": None
        }

    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return {
        "statusCode": 200,
        "status": True,
        "message": "Password reset successful.",
        "data": None
    }

# ======== UPDATE PASSWORD BY EMAIL FUNCTION ========
def update_password_by_email(db: Session, email: str, new_password: str, confirm_new_password: str) -> Dict:
    """
    Update password for user (parent or admin) by email. No current password required.
    """
    if new_password != confirm_new_password:
        return {
            "statusCode": 400,
            "status": False,
            "message": "New password and confirm password do not match.",
            "data": None
        }

    # Try to find user in Admin table first
    admin = db.execute(select(Admin).where(Admin.email == email.strip().lower())).scalars().first()
    if admin:
        admin.password = get_password_hash(new_password)
        db.commit()
        db.refresh(admin)
        return {
            "statusCode": 200,
            "status": True,
            "message": "Password updated successfully for admin.",
            "data": None
        }

    # Try to find user in User table
    user = db.execute(select(User).where(User.email == email.strip().lower())).scalars().first()
    if user:
        user.password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return {
            "statusCode": 200,
            "status": True,
            "message": "Password updated successfully for user.",
            "data": None
        }

    return {
        "statusCode": 404,
        "status": False,
        "message": "User with this email not found.",
        "data": None
    }

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
