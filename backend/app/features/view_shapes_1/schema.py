from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class FunctionItem(BaseModel):
    link_point_id:       int
    link_point_name:     str
    link_partition_id:   int
    link_ai_id:          Optional[int]
    link_partition_name: str
    formula_order:       int
    setValue:            int
    isTrue_operand_type: int
    isTrue:              int
    isFalse_operand_type:int
    isFalse:             int
    function_id:         int
    fu_operator_id:      int
    list_name:           str
    parameters:          int
    operator_name:       str

class ViewShapeResp(BaseModel):
    # ---- 主表欄位 ----
    view_id:               int
    view_name:             str
    view_height:           int
    view_width:            int
    view_backgroundColor:  str
    svg_tag:               str | None
    view_type:             int | None
    view_shape_id:         int | None
    view_shape_order:      int | None
    view_x:                int | None
    view_y:                int | None
    # ---- 元件 ----
    elem_id:               int | None
    elem_name:             str | None
    point_id:              int | None
    elem_link_URL:         str | None = None
    elem_view_id:          int | None = None
    isLock:                bool | None = None
    elem_view_type:        int | None = None
    # ---- 點位 & 區塊 ----
    point_name:            str | None
    di_id:                 int | None
    ai_id:                 int | None
    do_id:                 int | None
    sdi_id:                int | None
    partition_id:          int | None
    partition_name:        str | None
    # ---- 狀態 ----
    elem_shapes_id:        int | None
    status:                int | None
    statu_default:         bool | None
    shape_name_id:         int | None
    shapes_name:           str | None
    shapes_name_svg_tage:  str | None
    group_y:               int | None
    group_width:           int | None
    group_height:          int | None
    shapes_name_view_id:   int | None = None
    link_URL:              str | None = None
    # ---- shape 參數 ----
    shape_type:            int | None= None
    x:                     int | None= None
    y:                     int | None= None
    zoom:                  int | None= None
    is_popup:              bool | None= None
    is_shine:              bool | None= None
    tooltips:              str | None= None
    width:                 int | None= None
    height:                int | None= None
    fill_color:            str | None= None
    fill_style:            str | None= None
    border_color:          str | None= None
    border_width:          int | None= None
    angle:                 int | None= None
    group_order:           int | None= None
    shape_id:              int | None= None
    # ---- 子查詢 ----
    sub:        list = []
    function:   List[FunctionItem] = []
    do_list:    list = []

    model_config = ConfigDict(from_attributes=True)

