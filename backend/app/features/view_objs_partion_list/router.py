from fastapi import APIRouter, Depends, status
# from sqlalchemy.ext.asyncio import AsyncSession  
from .schema import ViewObj
from .crud import ViewObjCRUD

router = APIRouter(
    prefix="/ViewObjsPartionList",
    tags=["View Objs Partion List"],
)

@router.post(
    "",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="儲存 / 讀回 Partition List",
)
async def save_partion_list(
    body: list[str],
    # db: AsyncSession = Depends(get_db),   
):
    """
    1. 非同步寫入 JSON（取自 `.env` 的 `PARTITION_LIST_PATH`）\n
    2. 回傳同一份 list，確保前後端一致
    """
    row = await ViewObjCRUD.write(body)
    return row
