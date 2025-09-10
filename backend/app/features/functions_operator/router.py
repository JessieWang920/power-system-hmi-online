# backend/app/features/functions_operator/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import FOResp
from .crud import FOCrud
from app.core.db import get_db

router = APIRouter(prefix="/FUNCTIONS_OPERATOR", tags=["Functions Operator"])

@router.get("", response_model=List[FOResp])
async def read_functions_operator(
    fu_operator_id: int | None = Query(default=None, description="若帶入則單筆查詢"),
    db: AsyncSession = Depends(get_db),
):
    if fu_operator_id is None:
        data = await FOCrud.read_all(db)
        return data # FastAPI 會把 SQLAlchemy 物件自動轉 FOResp（因為 schema 設定了 from_attributes）
    
    obj = await FOCrud.read_by_id(db, fu_operator_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fu_operator_id={fu_operator_id} 不存在"
        )
    return [obj]
