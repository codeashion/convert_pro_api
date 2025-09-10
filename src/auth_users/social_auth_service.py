import logging
import firebase_admin
from firebase_admin import credentials, auth
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime
import os

from ..admin_users.models import User
from ..config import FIREBASE_CREDENTIALS_PATH, FIREBASE_PROJECT_ID
from .service import create_access_token

logger = logging.getLogger(__name__)

class FirebaseAuthService:
    """Service for handling Firebase Authentication"""
    
    def __init__(self):
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            logger.info("Firebase already initialized")
        except ValueError:
            # Firebase not initialized, initialize it
            if FIREBASE_CREDENTIALS_PATH and os.path.exists(FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'projectId': FIREBASE_PROJECT_ID
                })
                logger.info("Firebase initialized with service account")
            else:
                # For development, you can use default credentials
                firebase_admin.initialize_app()
                logger.info("Firebase initialized with default credentials")
    
    async def verify_firebase_token(self, id_token: str) -> Dict:
        """Verify Firebase ID token and extract user information"""
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            # Extract user information
            user_info = {
                "firebase_uid": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name", ""),
                "picture": decoded_token.get("picture", ""),
                "email_verified": decoded_token.get("email_verified", False),
                "provider": self._get_provider_from_token(decoded_token)
            }
            
            return user_info
            
        except auth.InvalidIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token"
            )
        except auth.ExpiredIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase token has expired"
            )
        except auth.RevokedIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase token has been revoked"
            )
        except Exception as e:
            logger.error(f"Firebase token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase authentication failed"
            )
    
    def _get_provider_from_token(self, decoded_token: Dict) -> str:
        """Extract the authentication provider from the token"""
        firebase_info = decoded_token.get("firebase", {})
        sign_in_provider = firebase_info.get("sign_in_provider", "unknown")
        
        # Map Firebase providers to our system
        provider_mapping = {
            "google.com": "google",
            "apple.com": "apple",
            "facebook.com": "facebook",
            "twitter.com": "twitter",
            "password": "email",
            "anonymous": "anonymous"
        }
        
        return provider_mapping.get(sign_in_provider, sign_in_provider)
    
    def find_or_create_user(self, db: Session, firebase_data: Dict) -> User:
        """Find existing user or create new one based on Firebase data"""
        try:
            firebase_uid = firebase_data["firebase_uid"]
            email = firebase_data["email"]
            
            # First try to find by Firebase UID
            user = db.execute(
                select(User).where(User.google_id == firebase_uid)  # Reusing google_id field for Firebase UID
            ).scalars().first()
            
            if user:
                # Update provider info if needed
                if user.provider != firebase_data["provider"]:
                    user.provider = firebase_data["provider"]
                    db.commit()
                return user
            
            # Try to find by email (existing user wanting to link Firebase)
            if email:
                user = db.execute(
                    select(User).where(User.email == email)
                ).scalars().first()
                
                if user:
                    # Link Firebase account to existing user
                    user.google_id = firebase_uid  # Store Firebase UID
                    user.provider = firebase_data["provider"]
                    db.commit()
                    db.refresh(user)
                    return user
            
            # Create new user
            new_user = User(
                full_name=firebase_data["name"] or "Firebase User",
                email=email or f"firebase_{firebase_uid}@temp.com",
                google_id=firebase_uid,  # Store Firebase UID in google_id field
                provider=firebase_data["provider"],
                password=None  # No password for social login
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"Created new Firebase user: {new_user.email}")
            return new_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating Firebase user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )

# Create service instance
firebase_auth_service = FirebaseAuthService()