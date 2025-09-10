# backend/app/features/views_menu_buttons/router.py
from fastapi import APIRouter, Depends, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security_basic import basic_auth
from .schema import VMBCreate, VMBUpdate, VMBDelete, VMBResp
from .crud import VMBCRUD

router = APIRouter(
    prefix="/VIEWS_MENU_BUTTONS",
    tags=["Views Menu Buttons"],
    
)

@router.post("", response_model=List[VMBResp], status_code=status.HTTP_201_CREATED)
async def create_vmb(payload: VMBCreate, db: AsyncSession = Depends(get_db)):
    row = await VMBCRUD.create(db, payload)
    return [VMBResp.model_validate(row)]

@router.get("", response_model=List[VMBResp])
async def read_vmb(menu_buttons_id: int | None = Query(None), db: AsyncSession = Depends(get_db)):
    rows = await VMBCRUD.read(db, menu_buttons_id)
    return [VMBResp.model_validate(r) for r in rows]

@router.put("", response_model=List[VMBResp])
async def update_vmb(payload: VMBUpdate, db: AsyncSession = Depends(get_db)):
    row = await VMBCRUD.update(db, payload)
    return [VMBResp.model_validate(row)]

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vmb(payload: VMBDelete, db: AsyncSession = Depends(get_db)):
    await VMBCRUD.delete(db, payload.menu_buttons_id)
