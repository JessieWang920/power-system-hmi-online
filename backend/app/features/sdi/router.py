from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.security_ip import ip_whitelist
from app.core.db import get_db
from .schema import (
    SDICreate, SDIUpdate, SDIDelete,
    SDIResp, SDIDetail, PartitionView
)
from .crud import SDICRUD

router = APIRouter(
    prefix="/SDI",
    tags=["SDI"],
    dependencies=[Depends(ip_whitelist)]
)

# ── Create ───────────────────────────────────────
@router.post("", response_model=list[SDIResp], status_code=status.HTTP_201_CREATED)
async def create_sdi(payload: SDICreate, db: AsyncSession = Depends(get_db)):
    row = await SDICRUD.create(db, payload)
    return [SDIResp.model_validate(row)]

# ── Read ─────────────────────────────────────────
@router.get("", response_model=List[SDIDetail | PartitionView])
async def list_sdi(
    sdi_id: int | None = Query(None),
    partition_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    if sdi_id is not None:
        rows = await SDICRUD.list_by_sdi(db, sdi_id)
        return [SDIDetail(**r) for r in rows]

    if partition_id is not None:
        rows = await SDICRUD.list_by_partition(db, partition_id)
        return [PartitionView(**r) for r in rows]

    return []

# ── Update ───────────────────────────────────────
@router.put("", response_model=list[SDIResp])
async def update_sdi(payload: SDIUpdate, db: AsyncSession = Depends(get_db)):
    row = await SDICRUD.update(db, payload)
    return [SDIResp.model_validate(row)]

# ── Delete ───────────────────────────────────────
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sdi(payload: SDIDelete, db: AsyncSession = Depends(get_db)):
    await SDICRUD.delete(db, payload)
