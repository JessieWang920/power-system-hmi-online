# backend/app/features/views_menu_main/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db           import get_db
from app.core.security_basic  import basic_auth
from .schema               import (
    MenuMainCreate, MenuMainResp, MenuMainUpdate, MenuMainDelete,MenuMainListResp
)
from .crud              import MenuMainCRUD

router = APIRouter(
    prefix="/VIEWS_MENU_MAIN",
    tags=["Views Menu Main"],
    # IP 白名單 + JWT 兩層保護
    dependencies=[Depends(basic_auth)]
)

# ───── POST ─────
@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=list[MenuMainResp])
async def create_menu(payload: MenuMainCreate, db: AsyncSession = Depends(get_db)):
    """新增 [dbo].[VIEWS_MENU_MAIN] 的資料"""
    mid = await MenuMainCRUD.create(db, payload)
    return [MenuMainResp(menu_main_id=mid)]

# ───── GET ─────
@router.get("", response_model=List[MenuMainListResp])
async def list_menu(db: AsyncSession = Depends(get_db)):
    """
    列出所有 [dbo].[VIEWS_MENU_MAIN]、[dbo].[VIEWS_MENU_BUTTONS]、[dbo].[VIEWS] 的詳細資訊"""
    return await MenuMainCRUD.list(db)

# ───── PUT ─────
@router.put("", response_model=list[MenuMainUpdate])
async def update_menu(payload: MenuMainUpdate, db: AsyncSession = Depends(get_db)):
    """更改 [dbo].[VIEWS_MENU_MAIN] 的資料"""
    row = await MenuMainCRUD.update(db, payload)
    return [MenuMainUpdate.model_validate(row)]

# ───── DELETE ─────
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(payload: MenuMainDelete, db: AsyncSession = Depends(get_db)):
    """刪除 [dbo].[VIEWS_MENU_MAIN] 的資料"""
    await MenuMainCRUD.delete(db, payload.menu_main_id)
