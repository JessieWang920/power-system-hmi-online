# backend/app/features/views/schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class _ViewBase(BaseModel):
    name: str
    height: int = 840
    width: int = 1760
    backgroundColor: str = "#ffffff"
    view_type: int = 1 # 1 圖面、2 跳窗
    svg_tag: Optional[str] = None


# --------- 讀取 ----------

class ViewRead(BaseModel):
    view_id: int
    name: str
    height: int
    width: int
    backgroundColor: str
    view_type: int

    model_config = ConfigDict(from_attributes=True)

# --------- 刪除 ----------
class ViewDelete(BaseModel):
    view_id: int

# --------- 建立 ----------
class ViewCreate(_ViewBase): pass

class ViewResp(_ViewBase):
    view_id: int
    model_config = ConfigDict(from_attributes=True)

# --------- 更新 ----------
class ViewUpdate(_ViewBase):
    view_id: int
