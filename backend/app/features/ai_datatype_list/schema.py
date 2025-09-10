from pydantic import BaseModel, ConfigDict
from typing import Optional

class AiDataTypeBase(BaseModel):    
    input_max:  Optional[float] = None    
    output_max: Optional[float] = None
    name: Optional[str] = None
    input_min:  Optional[float] = None
    output_min: Optional[float] = None

class AiDataTypeCreate(AiDataTypeBase):
    """POST：只需傳 name、input_max…等"""

class AiDataTypeUpdate(AiDataTypeBase):
    data_type_id: int

class AiDataTypeOut(AiDataTypeBase):
    data_type_id: Optional[int]
    model_config = ConfigDict(from_attributes=True)
