# backend/app/features/elements/schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class _ElementBase(BaseModel):
    point_id:  Optional[int]
    name:      str
    view_id:   Optional[int] = None
    link_URL:  Optional[str] = None
    isLock:    Optional[bool] = False

# ──────── Create ────────
class ElementCreate(_ElementBase): 
    # pass
    view_name: Optional[str] = None
    disabled:Optional[bool] = False

class ElementResp(_ElementBase):
    elem_id: int
    point_name:   Optional[str]=None
    
    model_config = ConfigDict(from_attributes=True)

# ──────── Update ────────
class ElementUpdate(_ElementBase):
    elem_id: int
    disabled:Optional[bool] = False

class ElementBinding(BaseModel):
    name: str
    elem_id: int
    link_URL: Optional[str] = None
    view_id: Optional[int]=None
    

# ──────── Delete ────────
class ElementDelete(BaseModel):
    elem_id: int

# ─────────── GET 請求 ───────────

class ElementShape(BaseModel):
    elem_shapes_id: int
    status:         int
    statu_default:  bool
    shape_name_id:  int
    shape_name:     str

# class ElementFull(ElementResp):
class ElementDetailResp(ElementResp):
    view_name: str | None = None
    point_name:   Optional[str]=None
    sub: List[ElementShape] = []
    model_config = ConfigDict(from_attributes=True)

 
class 	ElementListResp(BaseModel):
    elem_id:    int
    point_id:   Optional[int]  
    point_name:   Optional[str]=None  
    elem_name:  str
    link_URL:   Optional[str]
    view_id:    Optional[int]
    view_name:  Optional[str]
    isLock:     Optional[bool]

    model_config = ConfigDict(from_attributes=True)