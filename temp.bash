#!/bin/bash

# Set variables
BACKEND_DIR="backend_code"
SRC_DIR="$BACKEND_DIR/src"
MODULE_NAME="contractor_users"
MODULE_DIR="$SRC_DIR/$MODULE_NAME"

echo "Creating CRUD operations for Contractor Users..."

# Create directory structure if it doesn't exist
mkdir -p $MODULE_DIR

# Create auth.py for token verification
cat > $SRC_DIR/auth.py << 'EOL'
import jwt
from fastapi import HTTPException, status
from typing import Dict

from .config import SECRET_KEY, ALGORITHM

def verify_token(token: str) -> Dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided"
        )
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
EOL

# Create config.py
cat > $SRC_DIR/config.py << 'EOL'
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "fastapi_db")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
EOL

# Create database.py
cat > $SRC_DIR/database.py << 'EOL'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .config import DATABASE_URL

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
EOL

# Create schemas.py
cat > $SRC_DIR/schemas.py << 'EOL'
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# Contractor User schemas
class ContractorUserBase(BaseModel):
    name: str
    phone: str
    shift: Optional[str] = None
    station: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    firm_name: Optional[str] = None
    police_verification: Optional[bool] = False
    image: Optional[str] = None
    added_by: Optional[int] = None
    is_active: Optional[bool] = True

class ContractorUserCreate(ContractorUserBase):
    pass

class ContractorUserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    shift: Optional[str] = None
    station: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    firm_name: Optional[str] = None
    police_verification: Optional[bool] = None
    image: Optional[str] = None
    added_by: Optional[int] = None
    is_active: Optional[bool] = None

class ContractorUserInDB(ContractorUserBase):
    id: int
    created_at: datetime
    modify_at: datetime

    class Config:
        orm_mode = True

class ResponseModel(BaseModel):
    status: bool
    message: str
    data: Optional[Any] = None
EOL

# Create contractor_users/models.py
cat > $MODULE_DIR/models.py << 'EOL'
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from ..database import Base

class ContractorUser(Base):
    __tablename__ = "contractor_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    shift = Column(String(50))
    station = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    firm_name = Column(String(100))
    police_verification = Column(Boolean, default=False)
    image = Column(String(255))
    added_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    modify_at = Column(DateTime, default=func.now(), onupdate=func.now())
EOL

# Create contractor_users/service.py
cat > $MODULE_DIR/service.py << 'EOL'
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
from datetime import datetime

from ..auth import verify_token
from .models import ContractorUser
from ..schemas import ContractorUserCreate, ContractorUserUpdate

logger = logging.getLogger(__name__)

def create_contractor_user(db: Session, user_token: str, contractor_data: Dict) -> Dict:
    """
    Create a new contractor user
    """
    try:
        verify_token(user_token)
        
        new_contractor = ContractorUser(**contractor_data)
        db.add(new_contractor)
        db.commit()
        db.refresh(new_contractor)
        
        return {
            'status': True,
            'message': "Contractor user created successfully",
            'data': new_contractor
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in create_contractor_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contractor user: {str(e)}"
        )

def get_all_contractor_users(db: Session, user_token: str) -> Dict:
    """
    Get all contractor users
    """
    try:
        verify_token(user_token)
        
        contractors = db.execute(select(ContractorUser)).scalars().all()
        
        return {
            'status': True,
            'message': "Contractor users retrieved successfully",
            'data': contractors
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_all_contractor_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contractor users: {str(e)}"
        )

def get_contractor_user_by_id(db: Session, user_token: str, contractor_id: int) -> Dict:
    """
    Get a contractor user by ID
    """
    try:
        verify_token(user_token)
        
        contractor = db.execute(
            select(ContractorUser).where(ContractorUser.id == contractor_id)
        ).scalars().first()
        
        if not contractor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor user with ID {contractor_id} not found"
            )
            
        return {
            'status': True,
            'message': "Contractor user retrieved successfully",
            'data': contractor
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_contractor_user_by_id: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contractor user: {str(e)}"
        )

def update_contractor_user(db: Session, user_token: str, contractor_id: int, update_data: Dict) -> Dict:
    """
    Update a contractor user by ID
    """
    try:
        verify_token(user_token)
        
        # Check if contractor exists
        contractor = db.execute(
            select(ContractorUser).where(ContractorUser.id == contractor_id)
        ).scalars().first()
        
        if not contractor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor user with ID {contractor_id} not found"
            )
        
        # Update contractor
        update_data["modify_at"] = datetime.now()
        
        stmt = update(ContractorUser).where(ContractorUser.id == contractor_id).values(**update_data)
        db.execute(stmt)
        db.commit()
        
        # Get updated contractor
        updated_contractor = db.execute(
            select(ContractorUser).where(ContractorUser.id == contractor_id)
        ).scalars().first()
        
        return {
            'status': True,
            'message': "Contractor user updated successfully",
            'data': updated_contractor
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in update_contractor_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update contractor user: {str(e)}"
        )

def delete_contractor_user(db: Session, user_token: str, contractor_id: int) -> Dict:
    """
    Delete a contractor user by ID
    """
    try:
        verify_token(user_token)
        
        # Check if contractor exists
        contractor = db.execute(
            select(ContractorUser).where(ContractorUser.id == contractor_id)
        ).scalars().first()
        
        if not contractor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor user with ID {contractor_id} not found"
            )
        
        # Delete contractor
        stmt = delete(ContractorUser).where(ContractorUser.id == contractor_id)
        db.execute(stmt)
        db.commit()
        
        return {
            'status': True,
            'message': "Contractor user deleted successfully",
            'data': None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in delete_contractor_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete contractor user: {str(e)}"
        )
EOL

# Create contractor_users/views.py
cat > $MODULE_DIR/views.py << 'EOL'
from fastapi import APIRouter, Depends, Header, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Optional

from ..database import get_db
from . import service
from ..schemas import ContractorUserCreate, ContractorUserUpdate, ResponseModel

router = APIRouter(
    prefix="/contractor-users",
    tags=["contractor-users"]
)

@router.post("/", response_model=ResponseModel)
async def create_contractor_user(
    contractor_data: ContractorUserCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Create a new contractor user
    """
    return service.create_contractor_user(db, authorization, contractor_data.dict())

@router.get("/", response_model=ResponseModel)
async def get_all_contractor_users(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Get all contractor users
    """
    return service.get_all_contractor_users(db, authorization)

@router.get("/{contractor_id}", response_model=ResponseModel)
async def get_contractor_user(
    contractor_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Get a contractor user by ID
    """
    return service.get_contractor_user_by_id(db, authorization, contractor_id)

@router.put("/{contractor_id}", response_model=ResponseModel)
async def update_contractor_user(
    contractor_id: int,
    update_data: ContractorUserUpdate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Update a contractor user by ID
    """
    return service.update_contractor_user(db, authorization, contractor_id, update_data.dict(exclude_unset=True))

@router.delete("/{contractor_id}", response_model=ResponseModel)
async def delete_contractor_user(
    contractor_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Delete a contractor user by ID
    """
    return service.delete_contractor_user(db, authorization, contractor_id)
EOL

# Create or update api.py
cat > $SRC_DIR/api.py << 'EOL'
from fastapi import APIRouter

from .contractor_users.views import router as contractor_users_router
# Import other routers here as needed

router = APIRouter()

router.include_router(contractor_users_router)
# Include other routers here as needed
EOL

# Create or update main.py
cat > $SRC_DIR/main.py << 'EOL'
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contractor Management API",
    description="FastAPI application with MySQL database for contractor management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
EOL

# Create a requirements.txt file
cat > $BACKEND_DIR/requirements.txt << 'EOL'
fastapi>=0.95.0
uvicorn>=0.21.1
sqlalchemy>=2.0.9
pydantic>=1.10.7
python-dotenv>=1.0.0
pymysql>=1.0.3
cryptography>=40.0.1
python-jose>=3.3.0
python-multipart>=0.0.6
EOL

echo "CRUD operations created successfully!"
echo "To run the application, install dependencies and start the server:"
echo "cd $BACKEND_DIR"
echo "pip install -r requirements.txt"
echo "python -m src.main"