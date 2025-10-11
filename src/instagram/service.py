from sqlalchemy.orm import Session
from .model import Instagram, InstagramCreate, InstagramUpdate
from fastapi import HTTPException
from ..auth import verify_token

def create_instagram(db: Session, data: InstagramCreate, token: str):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	post = Instagram(
		image=data.image,
		date=data.date,
		time=data.time,
		caption=data.caption,
		post_status=data.post_status if data.post_status is not None else 0,
		user_id=user_id
	)
	db.add(post)
	db.commit()
	db.refresh(post)
	return post

def get_all_instagram(db: Session, token: str):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	return db.query(Instagram).filter(Instagram.user_id == user_id).all()

def get_instagram_by_id(db: Session, post_id: int, token: str):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	post = db.query(Instagram).filter(Instagram.id == post_id, Instagram.user_id == user_id).first()
	if not post:
		raise HTTPException(status_code=404, detail="Instagram post not found")
	return post

def update_instagram(db: Session, post_id: int, data: InstagramUpdate, token: str):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	post = db.query(Instagram).filter(Instagram.id == post_id, Instagram.user_id == user_id).first()
	if not post:
		raise HTTPException(status_code=404, detail="Instagram post not found")
	if data.image is not None:
		post.image = data.image
	if data.date is not None:
		post.date = data.date
	if data.time is not None:
		post.time = data.time
	if data.caption is not None:
		post.caption = data.caption
	if data.post_status is not None:
		post.post_status = data.post_status
	db.commit()
	db.refresh(post)
	return post

def delete_instagram(db: Session, post_id: int, token: str):
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	post = db.query(Instagram).filter(Instagram.id == post_id, Instagram.user_id == user_id).first()
	if not post:
		raise HTTPException(status_code=404, detail="Instagram post not found")
	db.delete(post)
	db.commit()
	return {"detail": "Instagram post deleted"}
