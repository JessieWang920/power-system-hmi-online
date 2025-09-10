# backend/app/features/views/router.py
from fastapi import APIRouter, Depends, HTTPException, Query ,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from app.core.security_ip import ip_whitelist
from app.core.db       import get_db
from .schema           import ViewCreate, ViewUpdate, ViewResp,ViewRead,ViewDelete
from .crud             import ViewCRUD


router = APIRouter(
    prefix="/VIEWS",
    tags=["Views"],
    dependencies=[Depends(ip_whitelist)]
)

# ------- POST -------
@router.post("", response_model=List[ViewResp], status_code=status.HTTP_201_CREATED)
async def create_view(payload: ViewCreate, db: AsyncSession = Depends(get_db)):
    row = await ViewCRUD.create(db, payload)
    return [ViewResp.model_validate(row)]

# ------- GET -------
@router.get("", response_model=List[Union[ViewResp,ViewRead]],status_code=status.HTTP_200_OK)
async def list_views(view_id: int | None = Query(None), db: AsyncSession = Depends(get_db)):
    if view_id is not None:
        row = await ViewCRUD.get_id(db, view_id)
        if row is None:
            raise HTTPException(status_code=404, detail="view_id 不存在")
        return [ViewRead.model_validate(row)]
    base = await ViewCRUD.get_all(db)
    return [ViewResp.model_validate(r, from_attributes=True) for r in base]

# ------- PUT -------
@router.put("", response_model=List[ViewResp],status_code=status.HTTP_200_OK)
async def update_view(payload: ViewUpdate, db: AsyncSession = Depends(get_db)):
    row = await ViewCRUD.update(db, payload)
    return [ViewResp.model_validate(row)]

# ------- DELETE -------
@router.delete("", status_code=status.HTTP_204_NO_CONTENT,summary="刪除 view 及其view_shapes")
async def delete_view(payload:ViewDelete, db: AsyncSession = Depends(get_db)):
    row = await ViewCRUD.delete(db, payload.view_id)
    # return [ViewResp.model_validate(row)]
