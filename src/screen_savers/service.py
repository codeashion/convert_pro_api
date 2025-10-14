
from .models import ScreenSaver, ScreenSaverCreate
from sqlalchemy.orm import Session
from ..auth import verify_token

def create_screen_saver(db: Session, data: ScreenSaverCreate, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    saver = ScreenSaver(
        image_url=data.image_url,
        user_id=user_id,
        select_status=data.select_status
    )
    db.add(saver)
    db.commit()
    db.refresh(saver)
    return saver

def get_screen_savers(db: Session, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    return db.query(ScreenSaver).filter(ScreenSaver.user_id == user_id).all()

def get_screen_saver_by_id(db: Session, saver_id: int, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    return db.query(ScreenSaver).filter(ScreenSaver.id == saver_id, ScreenSaver.user_id == user_id).first()

def update_screen_saver(db: Session, saver_id: int, data: ScreenSaverCreate, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    saver = db.query(ScreenSaver).filter(ScreenSaver.id == saver_id, ScreenSaver.user_id == user_id).first()
    if not saver:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(saver, key, value)
    db.commit()
    db.refresh(saver)
    return saver

def delete_screen_saver(db: Session, saver_id: int, token: str):
    token_data = verify_token(token)
    user_id = int(token_data.get("id"))
    saver = db.query(ScreenSaver).filter(ScreenSaver.id == saver_id, ScreenSaver.user_id == user_id).first()
    if not saver:
        return None
    db.delete(saver)
    db.commit()
    return True
