from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select
from ..home_essential.model import HomeEssential, HomeEssentialCreate, Grocery, GroceryCreate
from ..auth import verify_token

# Home Essentials CRUD Functions

def get_all_items(db: Session, token: str):
    """Get all home essential items"""
    verify_token(token)  # Just verify token, no user-specific filtering needed
    return db.execute(select(HomeEssential)).scalars().all()


def get_item_by_id(db: Session, item_id: int, token: str):
    """Get a specific home essential item by ID"""
    verify_token(token)
    item = db.get(HomeEssential, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Home essential item not found")
    return item


def add_item(db: Session, token: str, data: HomeEssentialCreate):
    """Add a new home essential item"""
    try:
        verify_token(token)
        
        # Check if item with same name already exists
        existing = db.execute(
            select(HomeEssential).where(HomeEssential.name == data.name)
        ).scalars().first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Home essential item with this name already exists")
        
        new_item = HomeEssential(name=data.name)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add home essential item: {str(e)}")


def update_item(db: Session, item_id: int, data: HomeEssentialCreate, token: str):
    """Update an existing home essential item"""
    try:
        verify_token(token)
        
        item = db.get(HomeEssential, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Home essential item not found")
        
        # Check if another item with same name already exists
        existing = db.execute(
            select(HomeEssential).where(
                HomeEssential.name == data.name,
                HomeEssential.id != item_id
            )
        ).scalars().first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Home essential item with this name already exists")
        
        item.name = data.name
        db.commit()
        db.refresh(item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update home essential item: {str(e)}")


def delete_item(db: Session, item_id: int, token: str):
    """Delete a home essential item"""
    try:
        verify_token(token)
        
        item = db.get(HomeEssential, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Home essential item not found")
        
        db.delete(item)
        db.commit()
        return {
            "statusCode": 200,
            "status": True,
            "message": "Home essential item deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete home essential item: {str(e)}")


# Grocery CRUD Functions

def get_all_groceries(db: Session, token: str):
    """Get all grocery items"""
    verify_token(token)  # Just verify token, no user-specific filtering needed
    return db.execute(select(Grocery)).scalars().all()


def get_grocery_by_id(db: Session, grocery_id: int, token: str):
    """Get a specific grocery item by ID"""
    verify_token(token)
    grocery = db.get(Grocery, grocery_id)
    if not grocery:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    return grocery


def add_grocery(db: Session, token: str, data: GroceryCreate):
    """Add a new grocery item"""
    try:
        verify_token(token)
        
        # Check if grocery with same name already exists
        existing = db.execute(
            select(Grocery).where(Grocery.name == data.name)
        ).scalars().first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Grocery item with this name already exists")
        
        new_grocery = Grocery(name=data.name)
        db.add(new_grocery)
        db.commit()
        db.refresh(new_grocery)
        return new_grocery
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add grocery item: {str(e)}")


def update_grocery(db: Session, grocery_id: int, data: GroceryCreate, token: str):
    """Update an existing grocery item"""
    try:
        verify_token(token)
        
        grocery = db.get(Grocery, grocery_id)
        if not grocery:
            raise HTTPException(status_code=404, detail="Grocery item not found")
        
        # Check if another grocery with same name already exists
        existing = db.execute(
            select(Grocery).where(
                Grocery.name == data.name,
                Grocery.id != grocery_id
            )
        ).scalars().first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Grocery item with this name already exists")
        
        grocery.name = data.name
        db.commit()
        db.refresh(grocery)
        return grocery
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update grocery item: {str(e)}")


def delete_grocery(db: Session, grocery_id: int, token: str):
    """Delete a grocery item"""
    try:
        verify_token(token)
        
        grocery = db.get(Grocery, grocery_id)
        if not grocery:
            raise HTTPException(status_code=404, detail="Grocery item not found")
        
        db.delete(grocery)
        db.commit()
        return {
            "statusCode": 200,
            "status": True,
            "message": "Grocery item deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete grocery item: {str(e)}")
