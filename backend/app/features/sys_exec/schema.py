# backend/app/features/sys_exec/schema.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class RunScriptReq(BaseModel):
    filePath: str = Field(..., description="要執行的檔案完整路徑")
    

class RunScriptResp(BaseModel):
    message: int = 1  # 1=成功, 對齊你的 Node-RED 設計
