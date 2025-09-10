from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.security_ip import ip_whitelist
from app.core.db import get_db
from .schema import ViewShapeResp
from .crud import ViewShapeCRUD

router = APIRouter(prefix="/VIEW_SHAPES_2", tags=["View Shapes 2"],
                #    dependencies=[Depends(ip_whitelist)]
                   )

@router.get("", response_model=List[ViewShapeResp],response_model_exclude_none=False, status_code=status.HTTP_200_OK)
async def read_view_shapes(
    view_id: int = Query(..., description="必填。要查詢的 view_id"),
    db: AsyncSession = Depends(get_db)
):
    data = await ViewShapeCRUD.get_by_view(db, view_id)
    if not data:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "detail": f"view_id={view_id} 無資料",
                "data": None
            }
        )
    # if not data:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"view_id={view_id} 無資料")
    return [ViewShapeResp.model_validate(r, from_attributes=True) for r in data]
