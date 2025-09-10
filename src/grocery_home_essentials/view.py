from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..grocery_home_essentials.service import (
    get_user_list,
    update_user_list,
    clear_user_list
)
from ..grocery_home_essentials.model import UserGroceryHomeEssentialCreate, UserGroceryHomeEssentialUpdate, UserGroceryHomeEssentialOut

router = APIRouter(prefix="/grocery-home-essentials", tags=["grocery-home-essentials"])

@router.get("/", response_model=UserGroceryHomeEssentialOut)
def get_user_list_endpoint(db: Session = Depends(get_db), token: str = Header(...)):
    """Get parent's grocery & home essential list (one per parent)"""
    return get_user_list(db, token)

@router.put("/update", response_model=UserGroceryHomeEssentialOut)
def update_user_list_endpoint(data: UserGroceryHomeEssentialUpdate, db: Session = Depends(get_db), token: str = Header(...)):
    """Update parent's grocery & home essential list"""
    return update_user_list(db, token, data)

@router.delete("/clear")
def clear_user_list_endpoint(db: Session = Depends(get_db), token: str = Header(...)):
    """Clear all items from parent's grocery & home essential list"""
    return clear_user_list(db, token)