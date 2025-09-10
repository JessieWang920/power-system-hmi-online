from fastapi import APIRouter, Depends, status ,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.db import get_db
from .schema import (
    AICreate, AIUpdate,
    PointCreateResp, AIUpdateResp, AIDetail,AIDelete
)
from .crud import AICRUD

router = APIRouter(prefix="/AI", tags=["AI"])

@router.post("", response_model=list[PointCreateResp], status_code=status.HTTP_201_CREATED)
async def create_ai(data: AICreate, db: AsyncSession = Depends(get_db)):
    result = await AICRUD.create(db, data)
    return [result]


@router.get("", response_model=list[AIDetail], status_code=status.HTTP_200_OK)
async def get_ai(partition_id: int, db: AsyncSession = Depends(get_db)):
    return await AICRUD.list_by_partition(db, partition_id)

@router.put("", response_model=list[AIUpdateResp], status_code=status.HTTP_200_OK)
async def update_ai(data: AIUpdate, db: AsyncSession = Depends(get_db)):
    return [await AICRUD.update(db, data)]

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai(data:AIDelete, db: AsyncSession = Depends(get_db)):
    await AICRUD.delete(db, data)
