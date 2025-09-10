# backend/app/features/auth/router.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.security_jwt import create_access_token
from app.features.auth import crud, schema

router = APIRouter(prefix="/auth", tags=["auth"])
cfg = settings()


@router.post("/register", response_model=schema.User)
async def register_user(
    user_in: schema.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """註冊用戶，先確認帳號唯一，再新增資料到資料庫"""
    existing = await crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already registered")
    return await crud.create_user(db, user_in)

@router.post("/token", response_model=schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """JWT 登入機制，使用token驗證，供後續使用API"""
    # 驗證帳密
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 產生token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=cfg.token_expire_min),
    )
    return {"access_token": access_token, "token_type": "bearer"}
