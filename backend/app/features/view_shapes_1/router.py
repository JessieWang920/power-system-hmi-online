from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from app.core.security_ip import ip_whitelist
from .crud import ViewShapeCRUD
from .schema import ViewShapeResp

router = APIRouter(
    prefix="/VIEW_SHAPES_1", tags=["View Shapes 1"],
    # dependencies=[Depends(ip_whitelist)]
)

@router.get(
    "", summary="查詢 View 及其所有 Shapes 資訊，主要處理 element",
    response_model=List[ViewShapeResp], status_code=status.HTTP_200_OK
)
async def read_view_shapes(
    view_id: int = Query(..., description="視窗 ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    等同於 Node-RED `GET /SCADA/VIEW_SHAPES_1`；\
    傳入 view_id，回傳整包陣列資料。
    """
    return await ViewShapeCRUD.get_view_shapes(db, view_id)
