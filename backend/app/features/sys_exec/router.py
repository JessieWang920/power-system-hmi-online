# backend/app/features/sys_exec/router.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from .schema import RunScriptReq, RunScriptResp
from .service import run_external
from typing import Any

# 假設你已有 JWT 驗證依賴
# 在你專案可能是 from app.core.security import get_current_user
async def get_current_user():
    # 這裡只是範例：請換成你專案既有的 JWT 檢查
    return {"sub": "demo-user"}

router = APIRouter(prefix="/runScript", tags=["System Exec"])

@router.post("", response_model=RunScriptResp, status_code=status.HTTP_200_OK)
async def run_script(payload: RunScriptReq,):
    try:
        code = await run_external(payload.filePath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if code == 0:
        return {"message": 1}  # 成功
    else:
        raise HTTPException(status_code=500, detail="Script execution failed")
