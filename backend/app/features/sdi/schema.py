from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# ─── Create ───────────────────────────────────────
class SDICreate(BaseModel): 
    partition_id: int
    name: str

class SDIResp(BaseModel):
    sdi_id: int
    name:str
    point_id: int
    partition_id: int
    model_config = ConfigDict(from_attributes=True)

# ─── Update ───────────────────────────────────────
class SDIUpdate(BaseModel):
    name: str
    sdi_id: int

# ─── Delete ───────────────────────────────────────
class SDIDelete(BaseModel):
    sdi_id: int
    point_id: int

# ─── GET 詳細 ─────────────────────────────────────
class FormulaItem(BaseModel):
    fu_point_id:      int
    sdi_id:           int
    point_id:         int
    fu_formula_id:    int
    point_name:       str
    partition_id:     int
    partition_name:   str
    formula_order:    int
    setValue:         int
    isTrue_operand_type:  int
    isTrue:           int
    isFalse_operand_type: int
    isFalse:          int
    function_id:      int
    fu_operator_id:   int
    function_name:    str
    parameters:       int
    operator_name:    str

class SDIDetail(BaseModel):
    sdi_id:         int
    point_id:       int
    point_name:     str
    partition_id:   int
    partition_name: str
    sub: List[FormulaItem]

class ElementItem(BaseModel):
    elem_id:   int
    elem_name: str

class PartitionView(BaseModel):
    partition_name: str
    partition_id:   int
    point_id:       int
    point_name:     str
    sdi_id:         int
    elements:       List[ElementItem]
