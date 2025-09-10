import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "CalenderApp")


DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = "mysql+pymysql://root:@localhost/calender"

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dARsJZWhU3h5G787m0bHwVHYExZQU42qbDY9BM7WBZHbDM9ttFVxE3upvPxk")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(30*24*60)))  # 30 days

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
