# Get all home essentials with status True

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..home_essential.service import (
    get_all_items, get_item_by_id, add_item, update_item, delete_item, delete_true_home_essentials,
    get_all_groceries, get_grocery_by_id, add_grocery, update_grocery, delete_grocery, delete_true_groceries
)
from ..home_essential.model import HomeEssentialCreate, HomeEssentialOut, GroceryCreate, GroceryOut

# Home Essentials Router
router = APIRouter(prefix="/home-essentials", tags=["home-essentials"])


@router.get("/", response_model=list[HomeEssentialOut])
def get_all(db: Session = Depends(get_db), token: str = Header(...)):
    """Get all home essential items"""
    return get_all_items(db, token)


@router.get("/delete-true")
def delete_true_items(db: Session = Depends(get_db), token: str = Header(...)):
    """Delete all status true home essential items"""
    return delete_true_home_essentials(db, token)


@router.get("/{item_id}", response_model=HomeEssentialOut)
def get_by_id(item_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    """Get a home essential item by ID"""
    return get_item_by_id(db, item_id, token)

@router.post("/add", response_model=HomeEssentialOut)
def add(data: HomeEssentialCreate, db: Session = Depends(get_db), token: str = Header(...)):
    """Add a new home essential item"""
    return add_item(db, token, data)

@router.put("/{item_id}", response_model=HomeEssentialOut)
def update(item_id: int, data: HomeEssentialCreate, db: Session = Depends(get_db), token: str = Header(...)):
    """Update a home essential item"""
    return update_item(db, item_id, data, token)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    """Delete a home essential item"""
    return delete_item(db, item_id, token)

# Grocery Router
grocery_router = APIRouter(prefix="/groceries", tags=["groceries"])

@grocery_router.get("/", response_model=list[GroceryOut])
def get_all_groceries_endpoint(db: Session = Depends(get_db), token: str = Header(...)):
    """Get all grocery items"""
    return get_all_groceries(db, token)


@grocery_router.get("/delete-true")
def delete_true_items_groceries(db: Session = Depends(get_db), token: str = Header(...)):
    """Delete all status true grocery items"""
    return delete_true_groceries(db, token)


@grocery_router.get("/{grocery_id}", response_model=GroceryOut)
def get_grocery_by_id_endpoint(grocery_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    """Get a grocery item by ID"""
    return get_grocery_by_id(db, grocery_id, token)

@grocery_router.post("/add", response_model=GroceryOut)
def add_grocery_endpoint(data: GroceryCreate, db: Session = Depends(get_db), token: str = Header(...)):
    """Add a new grocery item"""
    return add_grocery(db, token, data)

@grocery_router.put("/{grocery_id}", response_model=GroceryOut)
def update_grocery_endpoint(grocery_id: int, data: GroceryCreate, db: Session = Depends(get_db), token: str = Header(...)):
    """Update a grocery item"""
    return update_grocery(db, grocery_id, data, token)

@grocery_router.delete("/{grocery_id}")
def delete_grocery_endpoint(grocery_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    """Delete a grocery item"""
    return delete_grocery(db, grocery_id, token)
