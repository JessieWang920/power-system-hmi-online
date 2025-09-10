# backend/app/features/functions_points/router.py
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from .schema import FPCreate, FPUpdate, FPDelete, FPResp, FPDetail
from .crud   import FPCRUD

router = APIRouter(
    prefix="/FUNCTIONS_POINTS",
    tags=["Functions Points"],
)

# ── POST ──────────────────────────────────────────
@router.post("", response_model=List[FPResp], status_code=status.HTTP_201_CREATED)
async def create_fp(payload: FPCreate, db: AsyncSession = Depends(get_db)):
    new_id = await FPCRUD.create(db, payload)
    return [FPResp(fu_point_id=new_id, **payload.model_dump())]

# ── GET?sdi_id= ────────────────────────────────────
@router.get("", response_model=List[FPDetail])
async def read_fp(sdi_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    rows = await FPCRUD.read_by_sdi(db, sdi_id)
    return [FPDetail(**r) for r in rows]

# ── PUT ────────────────────────────────────────────
@router.put("", response_model=List[FPResp])
async def update_fp(payload: FPUpdate, db: AsyncSession = Depends(get_db)):
    _ = await FPCRUD.update(db, payload)
    return [FPResp(**payload.model_dump())]

# ── DELETE ────────────────────────────────────────
@router.delete("", status_code=status.HTTP_200_OK)
async def delete_fp(payload: FPDelete, db: AsyncSession = Depends(get_db)):
    row = await FPCRUD.delete(db, payload.fu_point_id)
    return [row]      # 回傳同 Node-RED 刪除 OUTPUT 的型式
