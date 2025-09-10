import jwt
import logging
from fastapi import HTTPException, status
from typing import Dict
from .config import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

def verify_token(token: str) -> Dict:
    """Verify JWT token and return payload with detailed error messages"""
    if not token:
        logger.warning("Authentication attempt with missing token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required. Please login to get a valid token."
        )
    
    if not token.strip():
        logger.warning("Authentication attempt with empty token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token cannot be empty. Please provide a valid token."
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token verified successfully for user ID: {payload.get('id')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Authentication attempt with expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please login again to get a new token."
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Authentication attempt with invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token. Please login again to get a valid token."
        )
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error. Please try again later."
        )
