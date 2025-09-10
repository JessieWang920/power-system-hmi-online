# backend/app/core/security.py
"""
用法

@router.get("/", response_model=list[schema.Partition])
def list_partitions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),   # ← 驗證
):

"""
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.features.auth import crud as auth_crud, schema as auth_schema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
cfg = settings()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """產生 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=cfg.token_expire_min))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, cfg.jwt_secret_key, algorithm=cfg.jwt_algorithm)
    return token

async  def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> auth_schema.User:
    """從請求中的 Bearer Token 解出 JWT，取得目前登入用戶"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cfg.jwt_secret_key, algorithms=[cfg.jwt_algorithm])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await auth_crud.get_user_by_username(db, username)
    if not user:
        raise credentials_exception
    return user
