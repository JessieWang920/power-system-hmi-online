# backend/app/features/auth/model.py

from sqlalchemy import Column, Integer, String
from app.core.db import Base

class Users(Base):
    __tablename__ = "USERS"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
