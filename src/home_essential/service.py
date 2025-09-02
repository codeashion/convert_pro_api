from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select
from ..home_essential.model import  ShoppingItem, ShoppingItemCreate
from ..auth import verify_token
from datetime import datetime
 
3
def get_all_items(db: Session, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))

    return db.execute(
        select(ShoppingItem).where(ShoppingItem.user_id == user_id)
    ).scalars().all()


def get_item_by_id(db: Session, item_id: int, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))

    item = db.get(ShoppingItem, item_id)
    if not item or item.user_id != user_id:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")
    return item


def add_item(db: Session, token: str, data: ShoppingItemCreate):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))

    new_item = ShoppingItem(
        user_id=user_id,
        item_name=data.item_name,
        is_completed=data.is_completed
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def update_item(db: Session, item_id: int, data: ShoppingItemCreate, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))

    item = db.get(ShoppingItem, item_id)
    if not item or item.user_id != user_id:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")

    item.item_name = data.item_name
    item.is_completed = data.is_completed
    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))

    item = db.get(ShoppingItem, item_id)
    if not item or item.user_id != user_id:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")

    db.delete(item)
    db.commit()
    return {"status": True, "message": "Shopping item deleted successfully"}
