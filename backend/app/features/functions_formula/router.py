# backend/app/features/functions_formula/router.py
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.security_ip import ip_whitelist
from app.core.db import get_db
from .schema import FFCreate, FFUpdate, FFDelete, FFResp
from .crud import FFCRUD

router = APIRouter(
    prefix="/FUNCTIONS_FORMULA",
    tags=["Functions Formula"],
    dependencies=[Depends(ip_whitelist)]
)

@router.post("", response_model=List[FFResp], status_code=status.HTTP_201_CREATED)
async def create_formula(payload: FFCreate, db: AsyncSession = Depends(get_db)):
    row = await FFCRUD.create(db, payload)
    return [FFResp.model_validate(row)]

@router.put("", response_model=List[FFResp])
async def update_formula(payload: FFUpdate, db: AsyncSession = Depends(get_db)):
    row = await FFCRUD.update(db, payload)
    return [FFResp.model_validate(row)]

@router.delete("",  status_code=status.HTTP_204_NO_CONTENT) #response_model=List[FFResp],
async def delete_formula(payload: FFDelete, db: AsyncSession = Depends(get_db)):
    row = await FFCRUD.delete(db, payload.fu_formula_id)
    # return [FFResp.model_validate(row)]
