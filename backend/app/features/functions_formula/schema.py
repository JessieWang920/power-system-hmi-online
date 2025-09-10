# backend/app/features/functions_formula/schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class _BaseFF(BaseModel):
    formula_order: int
    fu_operator_id: Optional[int] = None
    setValue: Optional[int] = None
    isTrue_operand_type: Optional[int] = None
    isTrue: Optional[int] = None
    isFalse_operand_type: Optional[int] = None
    isFalse: Optional[int] = None
    function_id:Optional[int] = None # FIXME : 這個 optional ?

class FFCreate(_BaseFF):
    ...

class FFUpdate(_BaseFF):
    fu_formula_id: int

class FFDelete(BaseModel):
    fu_formula_id: int

class FFResp(_BaseFF):
    fu_formula_id: int
    model_config = ConfigDict(from_attributes=True)
