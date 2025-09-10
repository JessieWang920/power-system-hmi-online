# backend/app/features/ai_objects_text/schema.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class _Base(BaseModel):
    name: str = None
    font_family: str = Field(default="Microsoft JhengHei")
    font_style: Optional[str] = None
    font_size: Optional[int] = None
    text: Optional[str] = None
    font_color: Optional[str] = None
    point_id: Optional[int] = None
    unit: Optional[str] = None

# ──────── Create ────────
class AIObjectTextCreate(_Base):
    pass

class AIObjectTextResp(_Base):
    ai_objectText_id: int
    model_config = ConfigDict(from_attributes=True)

# ──────── Update ────────
class AIObjectTextUpdate(_Base):
    ai_objectText_id: int

class AIObjectTextUpdatePoint(BaseModel):
    ai_objectText_id: int
    point_id: Optional[int] = None

# ──────── Delete ────────
class AIObjectTextDelete(BaseModel):
    ai_objectText_id: int


# ──────── Detail（含 JOIN 資料）───────
# 因為 name 改名為 ai_objectText_name， 故不繼承
class AIObjectTextDetail(BaseModel):
    ai_objectText_id: int
    ai_objectText_name: str
    font_family: str = Field(default="Microsoft JhengHei")
    font_style: Optional[str] = None
    font_size: Optional[int] = None
    text: Optional[str] = None
    font_color: Optional[str] = None
    point_id: Optional[int] = None
    point_name: Optional[str] = None
    partition_id: Optional[int] = None
    ai_id: Optional[int] = None
    partition_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
