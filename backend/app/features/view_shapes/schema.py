# backend/app/features/view_shapes/schema.py
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---- Create ----
class VSCreate(BaseModel):
    view_shape_order:int
    x:int
    y:int
    view_id:int     
    originalIndex: int

    link_URL:      Optional[str] = None
    disabled:      Optional[bool] = None
    vgt_id:        Optional[int]  = None    
    vgtSelected:   Optional[bool] = None
    view_name:     Optional[str] = None

    shape_name_id: Optional[int]  = None  
    elem_id      : Optional[int]  = None   
    ai_objectText_id:Optional[int]  = None 


# class VSCreateShape(_VSCommon):    
#     shape_name   :str
#     svg_tag      :str
#     group_y      :int
#     group_width  :int 
#     group_height :int 

# class VSCreateElement(_VSCommon):
                            
#     elem_name   :str
#     point_id    :int

# class VSCreateObject(_VSCommon):                      
#     name            :str
#     font_family: str
#     font_style:    str
#     font_size:     int
#     text:          str
#     font_color:    str
#     point_id    :Optional[int]  = None  
#     unit:          Optional[str] = None

# # 供 router / crud 使用的聯合型別
# VSCreate = Union[VSCreateShape, VSCreateElement, VSCreateObject]



class VSResp(BaseModel):
    view_shape_id:int
    view_shape_order:int
    x:int
    y:int
    view_id:int
    elem_id:         Optional[int] = None
    shape_name_id:   Optional[int] = None
    ai_objectText_id:Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# ---- Update ----
class VSUpdate(BaseModel):
    view_shape_id:int
    view_shape_order:int
    x:int
    y:int
    shape_name_id:Optional[int] = None
class VSUpdateResp(BaseModel):
    view_shape_id:int
    view_shape_order:int
    x:int
    y:int
  
# ---- Delete ----
class VSDelete(BaseModel):
    view_shape_id:int
