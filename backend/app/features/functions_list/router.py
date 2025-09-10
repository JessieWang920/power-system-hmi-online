# backend/app/features/functions_list/router.py
from typing import List, Union
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security_ip import ip_whitelist
from .schema import (
    FunctionCreate, FunctionUpdate, FunctionDelete,
    FunctionResp, FunctionDetailResp,FunctionResp
)
from .crud import FunctionCRUD

router = APIRouter(
    prefix="/FUNCTIONS_LIST",
    tags=["Functions_List"],
)

# ── POST ────────────────────────────────────────────
@router.post("", response_model=list[FunctionResp], status_code=status.HTTP_201_CREATED)
async def create_function(payload: FunctionCreate, db: AsyncSession = Depends(get_db)):
    row = await FunctionCRUD.create(db, payload)
    return [FunctionResp.model_validate(row)]

# ── GET ─────────────────────────────────────────────
@router.get("", response_model=List[Union[FunctionDetailResp, FunctionResp]])
async def list_functions(
    function_id: int | None = Query(None), db: AsyncSession = Depends(get_db)
):
    if function_id is None:
        rows = await FunctionCRUD.get_all(db)
        return [FunctionResp.model_validate(r) for r in rows]

    result = await FunctionCRUD.get_id(db, function_id)
    if result is None:
        return []
    base, sub = result
    return [FunctionDetailResp(**{
        "function_id": base.function_id,
        "function_name": base.name,
        "parameters": base.parameters,
        "sub": sub
    })]

# ── PUT ─────────────────────────────────────────────
@router.put("", response_model=list[FunctionResp])
async def update_function(payload: FunctionUpdate, db: AsyncSession = Depends(get_db)):
    row = await FunctionCRUD.update(db, payload)
    return [FunctionResp.model_validate(row)]

# ── DELETE ──────────────────────────────────────────
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_function(payload: FunctionDelete, db: AsyncSession = Depends(get_db)):
    await FunctionCRUD.delete(db, payload.function_id)
