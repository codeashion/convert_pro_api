from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .service import get_today_quote
from .model import DailyQuoteOut
from ..database import get_db

router = APIRouter(prefix="/daily-quotes", tags=["daily-quotes"])

@router.get("/today", response_model=DailyQuoteOut)
def get_today_quote_endpoint(db: Session = Depends(get_db)):
	return get_today_quote(db)
