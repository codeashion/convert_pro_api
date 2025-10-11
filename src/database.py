from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import os
# from .config import DATABASE_URL
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# DB_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "7x?FRp@+nZ"))
# DB_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "5fKxd2*Ce6&"))


load_dotenv()
# Database configuration
DB_USER = os.getenv("DB_USER", "sqlyog_user")
DB_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "StrongPassword123!"))
DB_HOST = os.getenv("DB_HOST", "168.231.71.192")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "calendar_db")

print("DB_USER :: ", DB_USER)
print("DB_PASSWORD :: ", DB_PASSWORD)
print("DB_HOST :: ", DB_HOST)
print("DB_PORT :: ", DB_PORT)
print("DB_NAME :: ", DB_NAME)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
