from sqlalchemy.orm import Session
from .model import DailyQuote, DailyQuoteOut
from datetime import date
from fastapi import HTTPException

def get_today_quote(db: Session) -> DailyQuoteOut:
	# Get all quotes ordered by id
	quotes = db.query(DailyQuote).order_by(DailyQuote.id).all()
	if not quotes:
		raise HTTPException(status_code=404, detail="No quotes found")
	# Use day of year (1-365) to select quote, cycling if > 365
	day_of_year = date.today().timetuple().tm_yday
	index = (day_of_year - 1) % len(quotes)
	return quotes[index]
