from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .service import create_photo, get_all_photos, get_photo_by_id, update_photo, delete_photo
from .model import PhotoCreate, PhotoUpdate, PhotoOut
from ..database import get_db
from ..auth import verify_token

router = APIRouter(prefix="/photos", tags=["photos"])

@router.post("/", response_model=PhotoOut)
def create_photo_endpoint(photo: PhotoCreate, db: Session = Depends(get_db), token: str = Header(...)):
	verify_token(token)
	return create_photo(db, photo)

@router.get("/", response_model=list[PhotoOut])
def get_photos_endpoint(db: Session = Depends(get_db), token: str = Header(...)):
	verify_token(token)
	return get_all_photos(db)

@router.get("/{photo_id}", response_model=PhotoOut)
def get_photo_endpoint(photo_id: int, db: Session = Depends(get_db), token: str = Header(...)):
	verify_token(token)
	return get_photo_by_id(db, photo_id)

@router.put("/{photo_id}", response_model=PhotoOut)
def update_photo_endpoint(photo_id: int, photo: PhotoUpdate, db: Session = Depends(get_db), token: str = Header(...)):
	verify_token(token)
	return update_photo(db, photo_id, photo)

@router.delete("/{photo_id}")
def delete_photo_endpoint(photo_id: int, db: Session = Depends(get_db), token: str = Header(...)):
	verify_token(token)
	return delete_photo(db, photo_id)
