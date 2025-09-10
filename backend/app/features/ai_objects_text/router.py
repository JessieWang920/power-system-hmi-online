# backend/app/features/ai_objects_text/router.py
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Query, status, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security_ip import ip_whitelist

from .schema import *
from .crud import AIObjectsTextCRUD

router = APIRouter(
    prefix="/AI_OBJECTS_TEXT",  # 前端路徑 = /SCADA + 這段  (見 config.api_prefix)
    tags=["AI Objects Text"],
    dependencies=[Depends(ip_whitelist)],
)

# ───── POST ─────
@router.post("", response_model=List[AIObjectTextResp], status_code=status.HTTP_201_CREATED)
async def create_ai_obj(payload: AIObjectTextCreate, db: AsyncSession = Depends(get_db)):
    row = await AIObjectsTextCRUD.create(db, payload)
    return [AIObjectTextResp.model_validate(row)]

# ───── GET (普通列表 / joined 詳細) ─────
@router.get("", response_model=List[Union[AIObjectTextDetail, AIObjectTextResp]])
async def list_ai_objs(
    ai_objectText_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    status_code=status.HTTP_200_OK
):
    if ai_objectText_id:
        try:
            ids: List[int] = [
                int(x) for x in ai_objectText_id.split(",") if x.strip()
            ]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="ai_objectText_id 必須為整數或用逗號分隔"
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="ai_objectText_id 必須為整數或用逗號分隔")
        return await AIObjectsTextCRUD.get_id(db, ids)

    rows = await AIObjectsTextCRUD.get_all(db)
    return [AIObjectTextResp.model_validate(r) for r in rows]

# ───── PUT ─────
@router.put("", response_model=List[AIObjectTextResp])
async def update_ai_obj(payload: Union[AIObjectTextUpdatePoint, AIObjectTextUpdate], 
                        db: AsyncSession = Depends(get_db), 
                        status_code=status.HTTP_200_OK):
    # 1. 把 payload 轉 dict，並去掉沒傳入的欄位
    data = payload.model_dump(
        # exclude_none=True #  null 的值排掉
        exclude_unset=True,   # 只包含使用者有傳的 key
        )
    keys = set(data.keys())
    # 2. 綁定點位，判斷只更新 point_id 的條件：payload 只有 ai_objectText_id + point_id
    if keys == {"ai_objectText_id", "point_id"}:
        # 建立一個只有這兩欄位的 Pydantic 模型
        point_only = AIObjectTextUpdatePoint(**data)
        row = await AIObjectsTextCRUD.update_point(db, point_only)
    else:
        row = await AIObjectsTextCRUD.update(db, payload)
    # 3. 直接回傳 ORM instance 列表，FastAPI 會自動用 response_model 序列化
    return [row]


# ───── DELETE ─────
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_obj(payload:AIObjectTextDelete, db: AsyncSession = Depends(get_db)):
    await AIObjectsTextCRUD.delete(db, payload.ai_objectText_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)