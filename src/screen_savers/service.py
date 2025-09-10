from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status, UploadFile
from typing import List
from ..screen_savers.models import ScreenSaver, ScreenSaverCreate, ScreenSaverUpdate, ScreenSaverOut
from ..file_upload.service import save_uploaded_file


def list_screen_savers(db: Session, limit: int = 100, offset: int = 0) -> List[ScreenSaverOut]:
    try:
        rows = db.execute(
            select(ScreenSaver).order_by(ScreenSaver.created_at.desc()).limit(limit).offset(offset)
        ).scalars().all()
        return [ScreenSaverOut.from_orm(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list screen savers: {str(e)}")


def get_screen_saver(db: Session, item_id: int) -> ScreenSaverOut:
    row = db.execute(select(ScreenSaver).where(ScreenSaver.id == item_id)).scalars().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screen saver not found")
    return ScreenSaverOut.from_orm(row)


def create_screen_saver(db: Session, payload: ScreenSaverCreate) -> ScreenSaverOut:
    row = ScreenSaver(image_url=payload.image_url)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ScreenSaverOut.from_orm(row)


async def create_screen_saver_from_upload(db: Session, file: UploadFile) -> ScreenSaverOut:
    """Upload an image and create a screen saver entry using its URL."""
    saved = await save_uploaded_file(db, file, category='screen_savers')
    row = ScreenSaver(image_url=saved.file_url)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ScreenSaverOut.from_orm(row)


def update_screen_saver(db: Session, item_id: int, payload: ScreenSaverUpdate) -> ScreenSaverOut:
    row = db.execute(select(ScreenSaver).where(ScreenSaver.id == item_id)).scalars().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screen saver not found")
    row.image_url = payload.image_url
    db.commit()
    db.refresh(row)
    return ScreenSaverOut.from_orm(row)


def delete_screen_saver(db: Session, item_id: int) -> dict:
    row = db.execute(select(ScreenSaver).where(ScreenSaver.id == item_id)).scalars().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screen saver not found")
    db.delete(row)
    db.commit()
    return {"statusCode": 200, "status": True, "message": "Screen saver deleted", "data": None}


