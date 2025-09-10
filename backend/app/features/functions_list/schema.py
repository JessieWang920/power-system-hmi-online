# backend/app/features/functions_list/schema.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

# ──────── Base ────────
class _FunctionBase(BaseModel):
    function_name: str
    parameters: Optional[int] = None

# ──────── Create ────────
class FunctionCreate(_FunctionBase):
    pass

class FunctionCreateResp(BaseModel):
    function_id: int

# ──────── Update ────────
class FunctionUpdate(_FunctionBase):
    function_id: int
    
# ──────── Delete ────────
class FunctionDelete(BaseModel):
    function_id: int

# ──────── GET·detail ────────
class FunctionResp(BaseModel):    
    parameters: Optional[int] = None
    function_id: int
    # 只指定輸入別名, 資料庫欄位名稱為 name，輸出為 function_name
    function_name: str  = Field(validation_alias="name")  
    model_config = ConfigDict(from_attributes=True)


class FunctionFormula(BaseModel):
    fu_formula_id: int
    formula_order: int
    setValue: Optional[int]
    isTrue_operand_type: Optional[int]
    isTrue: Optional[int]
    isFalse_operand_type: Optional[int]
    isFalse: Optional[int]
    fu_operator_id: int
    fu_operator_name: str

class FunctionDetailResp(FunctionResp):
    # 只指定輸入別名, 資料庫欄位名稱為 name，輸出為 function_name
    function_name: str
    parameters: Optional[int] = None
    function_id: int 
    sub: List[FunctionFormula] = []
