from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from .schema import (
    AiDataTypeCreate, AiDataTypeOut, AiDataTypeUpdate
)
from typing import Optional,Union
from .crud import AiDataTypeCRUD

router = APIRouter(prefix="/AI_DATATYPE_LIST",tags=["AI Data Types"],)

@router.post("", response_model=AiDataTypeOut, status_code=status.HTTP_201_CREATED)
async def create_ai_datatype(
    payload: AiDataTypeCreate, db: AsyncSession = Depends(get_db)
):
    return await AiDataTypeCRUD.create(db, payload)

# node-red 版本
# @router.get("", response_model=list[AiDataTypeOut])
# async def list_ai_datatypes(db: AsyncSession = Depends(get_db)):
#     return await AiDataTypeCRUD.get_all(db)

# @router.get("/{dt_id}", response_model=AiDataTypeOut)
# async def get_ai_datatype(
#     dt_id: int, db: AsyncSession = Depends(get_db)
# ):
#     obj = await AiDataTypeCRUD.get(db, dt_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="dataType_id not found")
#     return obj

@router.get("", response_model=Union[list[AiDataTypeOut], AiDataTypeOut])
async def read_ai_datatypes(
    id: Optional[int] = Query(None, alias="id"),
    db: AsyncSession = Depends(get_db),
):
    if id is None:
        return await AiDataTypeCRUD.get_all(db)
    obj = await AiDataTypeCRUD.get(db, id)
    if not obj:
        raise HTTPException(404, "dataType_id not found")
    return obj


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
async def edit_ai_datatype(
    payload: AiDataTypeUpdate, db: AsyncSession = Depends(get_db)
):
    success = await AiDataTypeCRUD.update(db, payload)
    if not success:
        raise HTTPException(status_code=404, detail="dataType_id not found")


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_datatype(
    id: int = Query(..., alias="id"),
    db: AsyncSession = Depends(get_db),
):
    success = await AiDataTypeCRUD.delete(db, id)
    if not success:
        raise HTTPException(404, "dataType_id not found")