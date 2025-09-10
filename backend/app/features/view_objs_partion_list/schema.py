# 接收與回傳格式相同
from pydantic import BaseModel

class ViewObj(BaseModel):
    payload: list[str] 
