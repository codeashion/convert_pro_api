from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ======================
# DATABASE CONFIG
# ======================

DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "convertpro"

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ======================
# SQLALCHEMY ENGINE
# ======================

engine = create_engine(
    DATABASE_URL,
    echo=True,           # Set False in production
    pool_pre_ping=True
)

# ======================
# SESSION
# ======================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ======================
# BASE MODEL
# ======================

Base = declarative_base()

# ======================
# DEPENDENCY
# ======================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
