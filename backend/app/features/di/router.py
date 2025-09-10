# backend/app/features/di/router.py
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from app.core.security_ip  import ip_whitelist
from app.core.security_jwt import get_current_user
from .schema import DiCreateIn, PointsRowOut, DIDetail, DiUpdateIn, DiDeleteIn
from .crud import DiCRUD

router = APIRouter(prefix="/DI", tags=["DI"])#, dependencies=[Depends(ip_whitelist), Depends(get_current_user)])

@router.post("", response_model=List[PointsRowOut], status_code=status.HTTP_201_CREATED)
async def create_di(payload: DiCreateIn, db: AsyncSession = Depends(get_db)):
    row = await DiCRUD.create(db, payload)
    return [PointsRowOut(**row)]

@router.get("", response_model=List[DIDetail])
async def list_di(partition_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    return await DiCRUD.list_by_partition(db, partition_id)

@router.put("", response_model=List[PointsRowOut])
async def update_di(payload: DiUpdateIn, db: AsyncSession = Depends(get_db)):
    try:
        row = await DiCRUD.update_one(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return [PointsRowOut(**row)]

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_di(payload: DiDeleteIn, db: AsyncSession = Depends(get_db)):
    await DiCRUD.delete_one(db, di_id=payload.di_id, point_id=payload.point_id, partition_id=payload.partition_id)
