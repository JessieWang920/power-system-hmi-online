from pydantic import BaseModel, ConfigDict
from typing import Optional
from typing import List


class PartitionBase(BaseModel):
    """基底欄位(共用欄位)"""
    name: str

class PartitionCreate(PartitionBase):
    """
    POST
    只需要 name 欄位
    不需要 partition_id，自動生成    
    """
    pass

class PartitionUpdate(PartitionBase):
    """PUT(name、partition_id欄位都需要)"""
    partition_id: int

class PartitionDelete(BaseModel):
    partition_id: int

class PartitionOut(PartitionBase):
    """回傳資料時要包含partition_id，所以這是前端拿到的完整資料格式"""
    partition_id: int
    model_config = ConfigDict(from_attributes=True)

class PartitionWithPoints(BaseModel):
    """含有點位資訊的欄位（平坦結構，與 POINTS JOIN 後的每行回傳結果）"""
    partition_name: str
    partition_id: int
    point_name: Optional[str] = None
    point_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        exclude_none=True  # 若欄位為 None，回應時自動去除該欄位
    )

