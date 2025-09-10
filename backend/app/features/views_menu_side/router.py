from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from .schema import (
    SideCreate,
    SideCreatedResp,
    SideUpdate,
    SideResp,
    SideDetailResp,
    SideDelete
)
from .crud import SideCrud
from app.core.security_basic  import basic_auth
router = APIRouter(prefix="/VIEWS_MENU_SIDE", tags=["Views Menu Side"],dependencies=[Depends(basic_auth)])

# ---------- POST ----------
@router.post("", response_model=List[SideCreatedResp], status_code=status.HTTP_201_CREATED)
async def create_sides(
    payload: SideCreate,
    db: AsyncSession = Depends(get_db),
):
    msid = await SideCrud.create(db, payload)
    return [SideCreatedResp(menu_side_id=msid)]


# ---------- GET ----------
@router.get("", response_model=List[SideDetailResp])
async def read_sides(
    menu_main_id: int | None = Query(default=None),
    view_id: int | None = Query(default=None),
    view_name: str | None = Query(default=None),
    link_URL: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    rows = await SideCrud.read_all(
        db,
        menu_main_id=menu_main_id,
        view_id=view_id,
        view_name=view_name,
        link_URL=link_URL,
    )
    return rows

# ---------- PUT ----------
@router.put("", response_model=List[SideResp])
async def update_side(
    payload: SideUpdate,
    db: AsyncSession = Depends(get_db),
):
    row = await SideCrud.update_one(db, payload)
    if not row:
        raise HTTPException(status_code=404, detail="menu_side_id not found")
    return [row]


# ---------- DELETE ----------
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_side(
    payload : SideDelete,
    db: AsyncSession = Depends(get_db),
):
    await SideCrud.delete_one(db, payload.menu_side_id)
  