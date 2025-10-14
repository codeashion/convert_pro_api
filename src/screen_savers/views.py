from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .service import (
	create_screen_saver, get_screen_savers, get_screen_saver_by_id,
	update_screen_saver, delete_screen_saver
)
from .models import ScreenSaverCreate, ScreenSaverOut
from ..database import get_db

router = APIRouter(prefix="/screen-savers", tags=["screen-savers"])

@router.post("/", response_model=ScreenSaverOut)
def create_saver(data: ScreenSaverCreate, db: Session = Depends(get_db), token: str = Header(...)):
	return create_screen_saver(db, data, token)

@router.get("/", response_model=list[ScreenSaverOut])
def list_savers(db: Session = Depends(get_db), token: str = Header(...)):
	return get_screen_savers(db, token)

@router.get("/{saver_id}", response_model=ScreenSaverOut)
def get_saver(saver_id: int, db: Session = Depends(get_db), token: str = Header(...)):
	saver = get_screen_saver_by_id(db, saver_id, token)
	if not saver:
		raise HTTPException(status_code=404, detail="Screen saver not found")
	return saver

@router.put("/{saver_id}", response_model=ScreenSaverOut)
def update_saver(saver_id: int, data: ScreenSaverCreate, db: Session = Depends(get_db), token: str = Header(...)):
	saver = update_screen_saver(db, saver_id, data, token)
	if not saver:
		raise HTTPException(status_code=404, detail="Screen saver not found")
	return saver

@router.delete("/{saver_id}")
def delete_saver(saver_id: int, db: Session = Depends(get_db), token: str = Header(...)):
	result = delete_screen_saver(db, saver_id, token)
	if not result:
		raise HTTPException(status_code=404, detail="Screen saver not found")
	return {"detail": "Screen saver deleted"}
