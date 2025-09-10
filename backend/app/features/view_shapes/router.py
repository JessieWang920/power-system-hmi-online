# backend/app/features/view_shapes/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db            import get_db
from app.core.security_ip   import ip_whitelist
from .schema                import VSCreate, VSUpdate, VSResp, VSDelete,VSUpdateResp
from .crud                  import VSCRUD

router = APIRouter(
    prefix="/VIEW_SHAPES",
    tags=["View Shapes"],
    dependencies=[Depends(ip_whitelist)],
)

@router.post("", response_model=List[VSResp], status_code=status.HTTP_201_CREATED)
async def create_vs(payload: List[VSCreate], db:AsyncSession=Depends(get_db)):
    row =  await VSCRUD.create(db, payload[0])
    return [VSResp.model_validate(row)]

@router.put("", response_model=List[VSUpdateResp])
async def update_vs(payload: List[VSUpdate], db:AsyncSession=Depends(get_db)):
    return await VSCRUD.update(db, payload)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vs(payload: VSDelete, db:AsyncSession=Depends(get_db)) -> None:
    await VSCRUD.delete(db, payload.view_shape_id)
