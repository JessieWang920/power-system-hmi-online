from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from .schema import ShapeCreate, ShapeResp, ShapeUpdate,ShapeDelete
from .crud import ShapeCRUD

router = APIRouter(prefix="/ELEMENTS_SHAPES", tags=["Element Shapes"])

@router.post("", response_model=List[ShapeResp], status_code=status.HTTP_201_CREATED)
async def create_shapes(payload: List[ShapeCreate] | ShapeCreate, db: AsyncSession = Depends(get_db)):
    rows = await ShapeCRUD.create(db, payload)
    return [ShapeResp.model_validate(r) for r in rows]

@router.put("", response_model=List[ShapeResp])
async def update_shape(payload: ShapeUpdate, db: AsyncSession = Depends(get_db)):
# async def update_shape(payload: ShapeCreate, elem_shapes_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    row = await ShapeCRUD.update(db, payload)
    return [ShapeResp.model_validate(row)]

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shape(payload:ShapeDelete, db: AsyncSession = Depends(get_db)):
    await ShapeCRUD.delete(db, payload.elem_shapes_id)
