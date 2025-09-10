# backend/app/features/view_shapes/router.py
from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.security_ip import ip_whitelist

from app.core.db import get_db
from .crud import ViewShapesCRUD
from .schema import ViewShapeResp

security = HTTPBasic()

# def verify_basic(credentials: HTTPBasicCredentials = Depends(security)):
#     """
#     範例 Basic Auth；正式環境可改存 DB / JWT
#     """
#     valid_user = "synin"
#     valid_pass = "s53709398"
#     if not (credentials.username == valid_user and credentials.password == valid_pass):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="驗證失敗")
#     return credentials.username

router = APIRouter(
    prefix="/VIEW_SHAPES_3",
    tags=["View Shapes 3"],
    # dependencies=[Depends(ip_whitelist)]
)

@router.get("", response_model=List[ViewShapeResp], status_code=status.HTTP_200_OK)
async def get_view_shapes(
    view_id: int = Query(..., description="要查詢的 view_id"),
    db: AsyncSession = Depends(get_db),
):
    rows = await ViewShapesCRUD.list_by_view_id(db, view_id)
    # Pydantic model_validate 助你轉成 list[ViewShapeResp]
    return [ViewShapeResp(**row) for row in rows]
