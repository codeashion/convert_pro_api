
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .service import create_instagram, get_all_instagram, get_instagram_by_id, update_instagram, delete_instagram
from .model import InstagramCreate, InstagramUpdate, InstagramOut
from ..database import get_db

router = APIRouter(prefix="/instagram", tags=["instagram"])

@router.post("/", response_model=InstagramOut)
def create_instagram_endpoint(
	data: InstagramCreate,
	db: Session = Depends(get_db),
	token: str = Header(...)
):
	return create_instagram(db, data, token)

@router.get("/", response_model=list[InstagramOut])
def get_instagram_endpoint(
	db: Session = Depends(get_db),
	token: str = Header(...)
):
	return get_all_instagram(db, token)

@router.get("/{post_id}", response_model=InstagramOut)
def get_instagram_by_id_endpoint(
	post_id: int,
	db: Session = Depends(get_db),
	token: str = Header(...)
):
	return get_instagram_by_id(db, post_id, token)

@router.put("/{post_id}", response_model=InstagramOut)
def update_instagram_endpoint(
	post_id: int,
	data: InstagramUpdate,
	db: Session = Depends(get_db),
	token: str = Header(...)
):
	return update_instagram(db, post_id, data, token)

@router.delete("/{post_id}")
def delete_instagram_endpoint(
	post_id: int,
	db: Session = Depends(get_db),
	token: str = Header(...)
):
	return delete_instagram(db, post_id, token)
