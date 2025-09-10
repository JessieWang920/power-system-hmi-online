from pydantic import BaseModel
from typing import Optional, List

# --- for POST ---
class DiCreateIn(BaseModel):
    partition_id: int
    point_name: str
    point_des: Optional[str] = None
    point_num: int

class PointsRowOut(BaseModel):
    point_id: int
    name: str
    partition_id: int
    di_id: int
    ai_id: Optional[int] = None
    do_id: Optional[int] = None
    sdi_id: Optional[int] = None

# --- for GET ?partition_id= ---
class Element(BaseModel):
    ai_objectText_id: Optional[int]
    ai_obj_name: Optional[str]
    unit: Optional[str]
    elem_id: Optional[int]
    elem_name:   Optional[str]
    
class DIDetail(BaseModel):
    point_id: int
    point_name: str
    partition_id: int
    partition_name: str
    di_id: int     
    point_num: int
    point_des: Optional[str] = None
    elements: List[Element]

# --- for PUT ---
class DiUpdateIn(BaseModel):
    di_id: int
    partition_id: int
    point_des: Optional[str] =None
    point_id: int
    point_name: str
    point_num: int

# --- for DELETE ---
class DiDeleteIn(BaseModel):
    partition_id: int
    point_id: int
    di_id: int
