
from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session
from ..auth_users.service import create_user, login_user, get_user_profile, update_user_profile, delete_user_profile, get_all_users, get_user_by_id, update_user_by_id, delete_user_by_id, create_access_token, reset_password
from ..admin_users.models import UserCreate, UserLogin, UserOut, ParentOut, FirebaseLoginRequest, FirebaseLoginResponse
from ..database import get_db
from ..auth import verify_token
from .social_auth_service import firebase_auth_service
from pydantic import BaseModel

class PasswordResetRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

class PasswordUpdateByEmailRequest(BaseModel):
    email: str
    new_password: str
    confirm_new_password: str
    
router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# ============ PUBLIC ENDPOINTS (NO TOKEN REQUIRED) ============

@router.post("/signup", response_model=dict)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (parent) with family members"""
    return create_user(db, user_data, role="parent")

@router.post("/login", response_model=dict)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Universal login for parents and admins"""
    return login_user(db, user_data)

@router.post("/firebase-login", response_model=FirebaseLoginResponse)
async def firebase_login(login_data: FirebaseLoginRequest, db: Session = Depends(get_db)):
    """Login with Firebase ID token (supports Google, Apple, Facebook, etc.)"""
    try:
        # Verify Firebase token and get user info
        firebase_user_data = await firebase_auth_service.verify_firebase_token(login_data.id_token)
        
        # Find or create user
        user = firebase_auth_service.find_or_create_user(db, firebase_user_data)
        
        # Create JWT token
        access_token = create_access_token({"id": user.id, "email": user.email, "role": "parent"})
        
        return FirebaseLoginResponse(
            message="Firebase login successful",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "parent": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "provider": user.provider
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firebase login failed: {str(e)}"
        )


@router.post("/reset-password", response_model=dict)
def reset_password_endpoint(request: PasswordResetRequest, db: Session = Depends(get_db), token: str = Header(...)):
    """Reset password for current user (parent or admin)"""
    return reset_password(db, token, request.current_password, request.new_password, request.confirm_new_password)


@router.post("/update-password-by-email", response_model=dict)
def update_password_by_email_endpoint(request: PasswordUpdateByEmailRequest, db: Session = Depends(get_db)):
    """Update password for user (parent or admin) by email. No current password required."""
    from ..auth_users.service import update_password_by_email
    return update_password_by_email(db, request.email, request.new_password, request.confirm_new_password)


# ============ PROTECTED ENDPOINTS (TOKEN REQUIRED) ============

@router.get("/profile", response_model=ParentOut)
def get_profile(db: Session = Depends(get_db), token: str = Header(...)):
    """Get current user profile"""
    return get_user_profile(db, token)

@router.put("/profile", response_model=ParentOut)
def update_profile(user_data: UserCreate, db: Session = Depends(get_db), token: str = Header(...)):
    """Update current user profile"""
    return update_user_profile(db, token, user_data)

@router.delete("/profile")
def delete_profile(db: Session = Depends(get_db), token: str = Header(...)):
    """Delete current user profile"""
    return delete_user_profile(db, token)

# ============ ADMIN-ONLY ENDPOINTS ============

@router.get("/parents", response_model=list[ParentOut])
def get_all_parents_endpoint(db: Session = Depends(get_db), token: str = Header(...)):
    """Get all parents (admin only)"""
    return get_all_users(db, token)

@router.get("/parents/{parent_id}", response_model=ParentOut)
def get_parent_by_id_endpoint(parent_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    """Get parent by ID (admin only)"""
    return get_user_by_id(db, token, parent_id)

@router.put("/parents/{parent_id}", response_model=ParentOut)
def update_parent_by_id_endpoint(parent_id: int, user_data: UserCreate, db: Session = Depends(get_db), token: str = Header(...)):
    """Update parent by ID (admin only)"""
    return update_user_by_id(db, token, parent_id, user_data)

@router.delete("/parents/{parent_id}")
def delete_parent_by_id_endpoint(parent_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    """Delete parent by ID (admin only)"""
    return delete_user_by_id(db, token, parent_id)