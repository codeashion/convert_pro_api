from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select
from typing import List, Dict
from datetime import datetime
from ..grocery_home_essentials.model import UserGroceryHomeEssential, UserGroceryHomeEssentialCreate, UserGroceryHomeEssentialUpdate
from ..home_essential.model import HomeEssential, Grocery
from ..auth import verify_token

def get_items_by_ids(db: Session, item_ids: List[int], model_class):
    """Helper function to get items by IDs"""
    if not item_ids:
        return []
    
    items = db.execute(
        select(model_class).where(model_class.id.in_(item_ids))
    ).scalars().all()
    
    return [{"id": item.id, "name": item.name} for item in items]

def parse_ids_string(ids_string: str) -> List[int]:
    """Convert comma-separated string to list of integers"""
    if not ids_string or ids_string.strip() == "":
        return []
    try:
        return [int(id_str.strip()) for id_str in ids_string.split(",") if id_str.strip()]
    except ValueError:
        return []

def ids_list_to_string(ids_list: List[int]) -> str:
    """Convert list of integers to comma-separated string"""
    return ",".join(str(id) for id in ids_list) if ids_list else ""

def get_user_list(db: Session, token: str) -> Dict:
    """Get the parent's grocery & home essential list (one per parent)"""
    payload = verify_token(token)
    user_id = int(payload["id"])
    
    # Get or create parent's list
    user_list = db.execute(
        select(UserGroceryHomeEssential).where(UserGroceryHomeEssential.user_id == user_id)
    ).scalars().first()
    
    # If no list exists, create a default one
    if not user_list:
        user_list = UserGroceryHomeEssential(
            user_id=user_id,
            home_essential_ids="",
            grocery_ids=""
        )
        db.add(user_list)
        db.commit()
        db.refresh(user_list)
    
    # Parse stored IDs
    home_essential_ids = parse_ids_string(user_list.home_essential_ids)
    grocery_ids = parse_ids_string(user_list.grocery_ids)
    
    # Get actual items from database
    home_essentials = get_items_by_ids(db, home_essential_ids, HomeEssential)
    groceries = get_items_by_ids(db, grocery_ids, Grocery)
    
    return {
        "id": user_list.id,
        "home_essentials": home_essentials,
        "groceries": groceries,
        "created_at": user_list.created_at or datetime.utcnow(),
        "updated_at": user_list.updated_at or datetime.utcnow()
    }

def update_user_list(db: Session, token: str, data: UserGroceryHomeEssentialUpdate) -> Dict:
    """Update the parent's grocery & home essential list"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        # Get parent's list
        user_list = db.execute(
            select(UserGroceryHomeEssential).where(UserGroceryHomeEssential.user_id == user_id)
        ).scalars().first()
        
        # If no list exists, create one first
        if not user_list:
            user_list = UserGroceryHomeEssential(
                user_id=user_id,
                home_essential_ids=ids_list_to_string(data.home_essential_ids or []),
                grocery_ids=ids_list_to_string(data.grocery_ids or [])
            )
            db.add(user_list)
            db.commit()
            db.refresh(user_list)
            return get_user_list(db, token)
        
        # Update home essential IDs if provided
        if data.home_essential_ids is not None:
            if data.home_essential_ids:
                home_items = db.execute(
                    select(HomeEssential).where(HomeEssential.id.in_(data.home_essential_ids))
                ).scalars().all()
                if len(home_items) != len(data.home_essential_ids):
                    raise HTTPException(status_code=400, detail="Some home essential items not found")
            
            user_list.home_essential_ids = ids_list_to_string(data.home_essential_ids)
        
        # Update grocery IDs if provided
        if data.grocery_ids is not None:
            if data.grocery_ids:
                grocery_items = db.execute(
                    select(Grocery).where(Grocery.id.in_(data.grocery_ids))
                ).scalars().all()
                if len(grocery_items) != len(data.grocery_ids):
                    raise HTTPException(status_code=400, detail="Some grocery items not found")
            
            user_list.grocery_ids = ids_list_to_string(data.grocery_ids)
        
        user_list.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user_list)
        
        # Return with full details
        return get_user_list(db, token)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user's grocery & home essential list: {str(e)}")

def clear_user_list(db: Session, token: str) -> Dict:
    """Clear all items from the parent's grocery & home essential list"""
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        
        # Get parent's list
        user_list = db.execute(
            select(UserGroceryHomeEssential).where(UserGroceryHomeEssential.user_id == user_id)
        ).scalars().first()
        
        if user_list:
            user_list.home_essential_ids = ""
            user_list.grocery_ids = ""
            user_list.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user_list)
        
        return {
            "statusCode": 200,
            "status": True,
            "message": "Parent's grocery & home essential list cleared successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear user's list: {str(e)}")
