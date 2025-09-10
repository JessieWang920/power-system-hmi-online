from pydantic import BaseModel, ConfigDict
from typing import Optional

class _Base(BaseModel):
    shape_name_id: Optional[int]
    elem_id:       Optional[int]
    status:        Optional[int]
    statu_default: bool = False

class ShapeCreate(_Base):
    shape_name:    Optional[str] 

class ShapeUpdate(_Base):
    shape_name:    Optional[str] 
    elem_shapes_id: Optional[int] = None

class ShapeDelete(BaseModel):
    elem_shapes_id: int


class ShapeResp(_Base):
    elem_shapes_id: int
    model_config = ConfigDict(from_attributes=True)
