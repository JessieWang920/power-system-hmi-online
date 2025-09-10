# backend/app/features/elements/router.py
from fastapi import APIRouter, Depends, status,  Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from fastapi.responses import PlainTextResponse
from app.core.security_ip import ip_whitelist
from app.core.db       import get_db
from .schema           import (
    ElementCreate, ElementUpdate, ElementResp, ElementDetailResp,ElementListResp,ElementDelete,ElementBinding
)
from .crud             import ElementCRUD

router = APIRouter(prefix="/ELEMENTS", tags=["Elements"], dependencies=[Depends(ip_whitelist)])

@router.post("", response_model=list[ElementResp], status_code=status.HTTP_201_CREATED)
async def create_element(payload: ElementCreate, db: AsyncSession = Depends(get_db)):
    row = await ElementCRUD.create(db, payload)
    return [ElementResp.model_validate(row)]

@router.get("", response_model=List[Union[ElementDetailResp, ElementListResp]])
async def list_elements(elem_id: int | None = Query(None), db: AsyncSession = Depends(get_db)):
    if elem_id is not None:
        data = await ElementCRUD.get_id(db, elem_id)
        return [ElementDetailResp(**data)]

    base = await ElementCRUD.get_all(db)
    return [ElementListResp.model_validate(r, from_attributes=True) for r in base]

@router.put("", response_model=list[ElementResp])
async def update_element(payload: Union[ElementUpdate,ElementBinding], db: AsyncSession = Depends(get_db)):
    if isinstance(payload, ElementBinding): # payload 來自跳窗設定
        row =  await ElementCRUD.update_view(db, payload)
    else:
        row = await ElementCRUD.update(db, payload)
    return [ElementResp.model_validate(row)]


@router.delete("", status_code=status.HTTP_204_NO_CONTENT,summary="刪除 element 及其狀態")
async def delete_element(payload: ElementDelete, db: AsyncSession = Depends(get_db)) -> None:
    await ElementCRUD.delete(db, payload.elem_id)    
