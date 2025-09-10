# backend/app/features/view_shapes/schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ViewShapeResp(BaseModel):
    # VIEWS
    view_id: int
    view_name: str
    view_height: int
    view_width: int
    view_backgroundColor: str
    # VIEW_SHAPES
    view_shape_id: int
    view_shape_order: int
    view_x: int
    view_y: int
    # AI_OBJECTS_TEXT
    ai_objectText_id: int
    ai_objectText_name: str
    font_family: str
    font_style: str
    font_size: int
    text: str
    font_color: str
    unit: Optional[str]
    # POINTS
    point_id: Optional[int]
    point_name: Optional[str]
    di_id: Optional[int]
    ai_id: Optional[int]
    do_id: Optional[int]
    sdi_id: Optional[int]
    # PARTITION / AI_DATATYPE
    partition_id: Optional[int]
    partition_name: Optional[str]
    dataType_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)
