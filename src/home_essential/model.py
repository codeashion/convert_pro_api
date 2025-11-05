# from sqlalchemy import Column, Integer, String, Boolean
# from pydantic import BaseModel
# from ..database import Base

# # SQLAlchemy model for Home Essentials (simplified to only id and name)
# class HomeEssential(Base):
#     __tablename__ = "home_essentials"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(200), nullable=False)
#     status = Column(Boolean, default=False, nullable=False)

# # Pydantic models
# class HomeEssentialCreate(BaseModel):
#     name: str
#     status: bool = False

# class HomeEssentialOut(BaseModel):
#     id: int
#     name: str
#     status: bool

#     class Config:
#         from_attributes = True

# # SQLAlchemy model for Grocery (simplified to only id and name)
# class Grocery(Base):
#     __tablename__ = "groceries"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(200), nullable=False)
#     status = Column(Boolean, default=False, nullable=False)

# # Pydantic models for Grocery
# class GroceryCreate(BaseModel):
#     name: str
#     status: bool = False

# class GroceryOut(BaseModel):
#     id: int
#     name: str
#     status: bool

#     class Config:
#         from_attributes = True
#     name: str

# class GroceryOut(BaseModel):
#     id: int
#     name: str
#     status: bool

#     class Config:
#         from_attributes = True


from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel
from ..database import Base

# ---------- SQLAlchemy Models ----------

class HomeEssential(Base):
    __tablename__ = "home_essentials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    status = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, nullable=False)  # Removed ForeignKey


class Grocery(Base):
    __tablename__ = "groceries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    status = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, nullable=False)  # Removed ForeignKey

# ---------- Pydantic Models ----------

class HomeEssentialCreate(BaseModel):
    name: str
    status: bool = False

class HomeEssentialOut(BaseModel):
    id: int
    name: str
    status: bool

    class Config:
        from_attributes = True


class GroceryCreate(BaseModel):
    name: str
    status: bool = False

class GroceryOut(BaseModel):
    id: int
    name: str
    status: bool

    class Config:
        from_attributes = True
