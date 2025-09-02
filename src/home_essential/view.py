from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..home_essential.service import (
    get_all_items,
    get_item_by_id,
    add_item,
    update_item,
    delete_item
)
from ..home_essential.model import ShoppingItemCreate, ShoppingItemOut

router = APIRouter(prefix="/home_essential-items", tags=["home_essential-items"])


@router.get("/", response_model=list[ShoppingItemOut])
def get_all(db: Session = Depends(get_db), token: str = Header(...)):
    return get_all_items(db, token)


@router.get("/{item_id}", response_model=ShoppingItemOut)
def get_by_id(item_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    return get_item_by_id(db, item_id, token)


@router.post("/add", response_model=ShoppingItemOut)
def add(data: ShoppingItemCreate, db: Session = Depends(get_db), token: str = Header(...)):
    return add_item(db, token, data)


@router.put("/{item_id}", response_model=ShoppingItemOut)
def update(item_id: int, data: ShoppingItemCreate, db: Session = Depends(get_db), token: str = Header(...)):
    return update_item(db, item_id, data, token)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    return delete_item(db, item_id, token)
