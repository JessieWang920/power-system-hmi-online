# backend/app/features/shapes_name/schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union,  List, Dict, Any

class ShapeNameBase(BaseModel):
    name: str
    group_width: float = 0
    group_height: float = 0
    # group_x: float = 0
    group_y: float = 0
    view_id: Optional[int] = None 
    # view_id: Optional[Union[int, str]] = None # 應該要只能 int正確

    link_URL: Optional[str] = None
    svg_tag: Optional[str] = None  # JSON array 字串

# ───── POST ─────
class ShapeNameCreate(ShapeNameBase):
    group_x: float = 0
    svgObjects: str #= Field(description="整段 <svg … /> 原始碼")  # 不存 DB，可先暫存 S3
    

class ShapeNameResp(BaseModel):
    name: str = Field(alias="shape_name") # 傳出去要看到 shape_name，就把 alias 寫成 "shape_name"
    shape_name_id: int
    group_width: float = 0
    group_height: float = 0
    # group_x: float = 0
    group_y: float = 0
    view_id: Optional[int] = None
    link_URL: Optional[str] = None
    svg_tag: Optional[str] = None  # JSON array 字串    
    view_name : Optional[str] = None  

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True # 接受用欄位名填值
                              )

# ───── PUT ─────
class ShapeNameUpdate(ShapeNameBase):
    shape_name_id: int
    old_name: str
    svgObjects: str
    model_config = ConfigDict(
        populate_by_name=True,  # 允許用欄位名稱 or alias 填值
    )

class ShapeNameUpdateBinding(BaseModel):
    name: str
    shape_name_id: int
    link_URL: Optional[str] = None
    view_id: Optional[int]=None
    
# ───── DELETE ─────
class ShapeNameDelete(BaseModel):
    shape_name_id: int
    name: str

class ShapeFull(BaseModel):
    # 來自 SHAPES_NAME
    shape_name:  str
    link_URL:    str | None = None
    view_id:     int | None = None
    view_name:   str | None = None
    svg_tag:     str | None = None
    shape_name_id: int

    # 來自 SHAPES
    shape_id:    int
    shape_type:  int
    x:           float
    y:           float
    zoom:        int
    is_popup:    bool
    is_shine:    bool
    tooltips:    str | None
    width:       float
    height:      float
    fill_color:  str | None
    fill_style:  str | None
    border_color:str | None
    border_width:int
    angle:       int
    group_order: int
    group_y:     float
    group_width: float
    group_height:float

    model_config = ConfigDict(from_attributes=True)