from pydantic import BaseModel, ConfigDict
from typing import Optional

class ViewShapeResp(BaseModel):
    view_id:                 int
    view_name:               str
    view_height:             int
    view_width:              int
    view_backgroundColor:    str
    view_shape_id:           int
    view_shape_order:        int
    view_x:                  int
    view_y:                  int

    shapes_name:             str
    svg_tag:                 Optional[str]
    group_y:                 int
    group_width:             int
    group_height:            int
    shapes_name_link_URL:    Optional[str]
    shapes_name_view_id:     Optional[int]
    shapes_name_view_type:   Optional[int]

    shape_id:                Optional[int] = None
    shape_name_id:           int
    shape_type:              Optional[int] = None
    x:                       Optional[int] = None
    y:                       Optional[int] = None
    zoom:                    Optional[int] = None
    is_popup:                Optional[bool] = False
    is_shine:                Optional[bool] = False
    tooltips:                Optional[str] = None
    width:                   Optional[int] = None
    height:                  Optional[int] = None
    fill_color:              Optional[str] = None
    fill_style:              Optional[str] = None
    border_color:            Optional[str] = None
    border_width:            Optional[int] = None
    angle:                   Optional[int] = None
    group_order:             Optional[int] = None

    model_config = ConfigDict(from_attributes=True,ser_json_exclude_none=False,)
