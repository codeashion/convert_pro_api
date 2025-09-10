from fastapi import APIRouter, Depends, UploadFile, File, Header
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..screen_savers.models import ScreenSaverCreate, ScreenSaverUpdate, ScreenSaverOut
from ..screen_savers.service import (
    list_screen_savers,
    get_screen_saver,
    create_screen_saver,
    update_screen_saver,
    delete_screen_saver,
)
from ..file_upload.service import save_uploaded_file
from ..screen_savers.user_screen_saver import UserScreenSaver, UserScreenSaverCreate, UserScreenSaverOut
from ..admin_users.models import User

router = APIRouter(prefix="/screen-savers", tags=["screen-savers"])

@router.get("/", response_model=List[ScreenSaverOut])
def list_screen_savers_endpoint(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return list_screen_savers(db, limit, offset)

@router.get("/selected", response_model=UserScreenSaverOut)
def get_selected_screen_saver(
    db: Session = Depends(get_db),
    token: str = Header(...)
):
    """Get selected screen saver for user"""
    from ..auth import verify_token
    user_data = verify_token(token)
    user_id = int(user_data["id"])
    mapping = db.query(UserScreenSaver).filter_by(user_id=user_id).first()
    if not mapping:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No screen saver selected for user")
    return mapping

@router.get("/{item_id}", response_model=ScreenSaverOut)
def get_screen_saver_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
):
    return get_screen_saver(db, item_id)

@router.post("/select", response_model=UserScreenSaverOut)
def select_screen_saver(
    payload: UserScreenSaverCreate,
    db: Session = Depends(get_db),
    token: str = Header(...)
):
    """Save selected screen saver for user"""
    from ..auth import verify_token
    user_data = verify_token(token)
    user_id = int(user_data["id"])
    # Remove previous selection if exists
    existing = db.query(UserScreenSaver).filter_by(user_id=user_id).first()
    if existing:
        db.delete(existing)
        db.commit()
    # Save new selection
    mapping = UserScreenSaver(user_id=user_id, screen_saver_id=payload.screen_saver_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping

@router.post("/add", response_model=ScreenSaverOut)
def create_screen_saver_endpoint(
    payload: ScreenSaverCreate,
    db: Session = Depends(get_db),
):
    return create_screen_saver(db, payload)
@router.post("/add", response_model=ScreenSaverOut)
def create_screen_saver_endpoint(
    payload: ScreenSaverCreate,
    db: Session = Depends(get_db),
):
    return create_screen_saver(db, payload)
from fastapi import APIRouter, Depends, UploadFile, File, Header
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..screen_savers.models import ScreenSaverCreate, ScreenSaverUpdate, ScreenSaverOut
from ..screen_savers.service import (
    list_screen_savers,
    get_screen_saver,
    create_screen_saver,
    update_screen_saver,
    delete_screen_saver,
)
from ..file_upload.service import save_uploaded_file
from ..screen_savers.user_screen_saver import UserScreenSaver, UserScreenSaverCreate, UserScreenSaverOut
from ..admin_users.models import User




router = APIRouter(prefix="/screen-savers", tags=["screen-savers"])

@router.post("/add", response_model=ScreenSaverOut)
def create_screen_saver_endpoint(
    payload: ScreenSaverCreate,
    db: Session = Depends(get_db),
):
    return create_screen_saver(db, payload)


@router.get("/", response_model=List[ScreenSaverOut])
def list_screen_savers_endpoint(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return list_screen_savers(db, limit, offset)


@router.get("/selected", response_model=UserScreenSaverOut)
def get_selected_screen_saver(
    db: Session = Depends(get_db),
    token: str = Header(...)
):
    """Get selected screen saver for user"""
    from ..auth import verify_token
    user_data = verify_token(token)
    user_id = int(user_data["id"])
    mapping = db.query(UserScreenSaver).filter_by(user_id=user_id).first()
    if not mapping:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No screen saver selected for user")
    return mapping

@router.get("/{item_id}", response_model=ScreenSaverOut)
def get_screen_saver_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
):
    return get_screen_saver(db, item_id)

@router.post("/select", response_model=UserScreenSaverOut)
def select_screen_saver(
    payload: UserScreenSaverCreate,
    db: Session = Depends(get_db),
    token: str = Header(...)
):
    """Save selected screen saver for user"""
    from ..auth import verify_token
    user_data = verify_token(token)
    user_id = int(user_data["id"])
    # Remove previous selection if exists
    existing = db.query(UserScreenSaver).filter_by(user_id=user_id).first()
    if existing:
        db.delete(existing)
        db.commit()
    # Save new selection
    mapping = UserScreenSaver(user_id=user_id, screen_saver_id=payload.screen_saver_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


