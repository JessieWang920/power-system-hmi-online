from fastapi import APIRouter, Depends, HTTPException, status ,Query
from typing import List  
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from .schema import *
from .crud import PartitionCRUD

# 這些路由網址會加上 /partition 開頭；tags 是給 Swagger UI 用的分類標籤
router = APIRouter(prefix="/PARTITION", tags=["Partition"])

# ── C ───────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=List[PartitionOut])
async def create_partition(
    data: PartitionCreate, db: AsyncSession = Depends(get_db)
    ):
    """
    新增資料POST：輸入 name，自動新增 partition_id 
    """
    pid = await PartitionCRUD.create(db, data)
    return [PartitionOut(partition_id=pid, **data.model_dump())]

# ── R ───────────────────────────────
# @router.get("", response_model=list[PartitionOut])
# async def list_partitions(db: AsyncSession = Depends(get_db)):
#     """
#     取得資料 GET：取得PATITION table 所有資料
#     """
#     return await PartitionCRUD.get_list(db)

# @router.get("{pid}", response_model=list[PartitionWithPoints])
# async def fetch_partition(pid: int, db: AsyncSession = Depends(get_db)):
#     data = await PartitionCRUD.get_id(db, pid)
#     if not data:
#         raise HTTPException(404, "partition_id not found")
#     return data



@router.get("",response_model=list[PartitionWithPoints], response_model_exclude_none=True)
async def fetch_partitions(
        id: Optional[int] = Query(
            None,
            alias="id",
            description= "不帶id ，回傳PATITION整張表；帶 id，回傳partion_id 該分區及其所有點位"
        ),
        db: AsyncSession = Depends(get_db)
    ) ->list[PartitionWithPoints]:
    if id is None:
        # 沒帶 ?id，就呼叫列出所有分區（這邊把每個 points 設成空清單）
        partitions = await PartitionCRUD.get_all(db)
        # PartitionCRUD.get_all 回傳 List[PartitionOut]
        # 我們把它轉成 PartitionWithPoints，points 填空：
        return [
            PartitionWithPoints(
                partition_id = p.partition_id,
                partition_name = p.name,
                # points = []   # no points
            )
            for p in partitions
        ]
    # 帶 ?id
    result = await PartitionCRUD.get_id(db, id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Partition {id} not found")
    return result  # List[PartitionWithPoints]

# ── U ───────────────────────────────
@router.put("", status_code=status.HTTP_200_OK)
async def edit_partition(
    data: PartitionUpdate, db: AsyncSession = Depends(get_db)
):
    """
    更新資料 PUT：輸入要更改的 name，成功更新一筆資料
    """
    await PartitionCRUD.update(db, data)


# ── D ───────────────────────────────
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def remove_partition(payload:PartitionDelete, db: AsyncSession = Depends(get_db)):
    await PartitionCRUD.delete(db, payload.partition_id)
