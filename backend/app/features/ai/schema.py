from pydantic import BaseModel
from typing import Optional, List

# ─────────── 共用欄位 ───────────
class AIBase(BaseModel):
    partition_id: int
    point_name: str
    point_min: float
    point_max: float

# ─────────── POST 請求 ───────────
class AICreate(AIBase):
    dataType_id: Optional[int] = 1  # TODO:待修正
    dataType_name: Optional[str] =None # 接收但不寫入 DB

# 回傳 POINTS INSERT 結果
class PointCreateResp(BaseModel):
    point_id: int
    name: str
    partition_id: int
    ai_id: int

# ─────────── PUT 請求 ───────────
class AIUpdate(AIBase):
    ai_id: int
    point_id: int
    dataType_id: Optional[int] = 1  # TODO:待修正
    dataType_name: Optional[str]

# 回傳 AI_LIST UPDATE 結果
class AIUpdateResp(BaseModel):
    dataType_id: int
    ai_min: float
    ai_max: float

# ─────────── GET/通用回傳 ───────────
class Element(BaseModel):
    ai_objectText_id: Optional[int] = None
    ai_obj_name: Optional[str] = None
    unit: Optional[str] = None

class AIDetail(BaseModel):
    point_id: int
    point_name: str
    partition_id: int
    partition_name: str
    ai_id: int
    dataType_id: int
    point_max: float
    point_min: float
    dataType_name: str
    inputMax: float
    ouptMax: float
    elements: List[Element]

# ─────────── DELETE 請求 ───────────
class AIDelete(BaseModel):
    partition_id: int
    tab_id: Optional[int] = None
    point_id: int
    ai_id: int

