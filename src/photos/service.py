from sqlalchemy.orm import Session
from .model import Photo, PhotoCreate, PhotoUpdate
from fastapi import HTTPException

def create_photo(db: Session, photo_data: PhotoCreate):
	photo = Photo(file=photo_data.file)
	db.add(photo)
	db.commit()
	db.refresh(photo)
	return photo

def get_all_photos(db: Session):
	return db.query(Photo).all()

def get_photo_by_id(db: Session, photo_id: int):
	photo = db.query(Photo).filter(Photo.id == photo_id).first()
	if not photo:
		raise HTTPException(status_code=404, detail="Photo not found")
	return photo

def update_photo(db: Session, photo_id: int, photo_data: PhotoUpdate):
	photo = db.query(Photo).filter(Photo.id == photo_id).first()
	if not photo:
		raise HTTPException(status_code=404, detail="Photo not found")
	if photo_data.file is not None:
		photo.file = photo_data.file
	db.commit()
	db.refresh(photo)
	return photo

def delete_photo(db: Session, photo_id: int):
	photo = db.query(Photo).filter(Photo.id == photo_id).first()
	if not photo:
		raise HTTPException(status_code=404, detail="Photo not found")
	db.delete(photo)
	db.commit()
	return {"detail": "Photo deleted"}
