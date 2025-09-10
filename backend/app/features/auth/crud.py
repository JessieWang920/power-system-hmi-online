# backend/app/features/auth/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.features.auth.schema import * 
from app.features.auth.model import Users
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_username(db: AsyncSession, username: str) -> Users | None:
    result = await db.execute(select(Users).where(Users.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate) -> Users:
    """新增用戶，密碼要加密"""
    hashed = pwd_context.hash(user_in.password)
    db_user = Users(username=user_in.username, hashed_password=hashed)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Users | None:
    user = await get_user_by_username(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user
