# backend/app/features/functions_operator/schema.py
from pydantic import BaseModel, Field, ConfigDict

class FOResp(BaseModel):
    fu_operator_id: int
    name: str = Field(..., max_length=50)

    model_config = ConfigDict(from_attributes=True)
