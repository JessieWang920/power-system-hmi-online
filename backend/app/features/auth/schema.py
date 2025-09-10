# backend/app/features/auth/schema.py

from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)   

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"