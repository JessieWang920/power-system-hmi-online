# backend/app/features/shapes_name/router.py
from fastapi import APIRouter, Depends, status, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union


from app.core.security_ip import ip_whitelist
from app.core.db import get_db
from .schema import (
    ShapeNameCreate, ShapeNameUpdate, ShapeNameResp, ShapeNameDelete, ShapeFull ,ShapeNameUpdateBinding
)
from .crud import ShapeNameCRUD

router = APIRouter(prefix="/SHAPES_NAME", tags=["Shapes Name"])
    
@router.post("", response_model=list[ShapeNameResp], status_code=status.HTTP_201_CREATED)
async def create_shape(
    payload: ShapeNameCreate,
    db: AsyncSession = Depends(get_db),
):
    """寫入DB，新增圖檔"""
    try:
        # 寫DB，寫檔案，其一錯誤即rollback
        async with db.begin():
            row = await ShapeNameCRUD.create(db, payload)
            await ShapeNameCRUD.create_pic(payload)

        return [ShapeNameResp.model_validate(row)]
    except HTTPException:
        raise


# @router.get("",  response_model=List[Union[ShapeFull, ShapeNameResp]])
@router.get("",  response_model=List[ShapeNameResp], status_code=status.HTTP_200_OK)
async def list_shape(
    shape_name_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db)
    ):
    # # 帶 id 取得全部資料，跳窗設定用
    # if shape_name_id is not None:
    #     data = await ShapeNameCRUD.full_detail(db, shape_name_id)
    #     return [ShapeFull(**r) for r in data]

    if shape_name_id is not None:
        base = await ShapeNameCRUD.get_by_id(db, shape_name_id)
        return [ShapeNameResp.model_validate(base, from_attributes=True)]
    
    # 沒帶 id，取得所有列表
    base = await ShapeNameCRUD.get_all(db)
    return [ShapeNameResp.model_validate(r, from_attributes=True) for r in base]


@router.put("", response_model=list[ShapeNameResp])
async def update_shape(payload: Union[ShapeNameUpdate,ShapeNameUpdateBinding], db: AsyncSession = Depends(get_db)):   
    """更新DB，更新圖檔"""
    try:
        
        if isinstance(payload, ShapeNameUpdateBinding): # payload 來自跳窗設定
            row = await ShapeNameCRUD.update_view(db, payload)            
        else: # payload 來自繪製圖面設定            
            async with db.begin(): # 寫DB，寫檔案，其一錯誤即rollback
                row = await ShapeNameCRUD.update(db, payload)
                await ShapeNameCRUD.update_pic(payload)
        return [ShapeNameResp.model_validate(row)]
    except HTTPException:
        raise


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shape(payload: ShapeNameDelete, db: AsyncSession = Depends(get_db)):
    """刪除DB，刪除圖檔"""

    async with db.begin():            
        await ShapeNameCRUD.delete(db, payload.shape_name_id)
        await ShapeNameCRUD.delete_pic(payload.name)
    



    
