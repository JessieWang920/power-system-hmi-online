# backend/app/features/ai_objects_text/crud.py
from typing import List, Sequence, Mapping, Any

from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.core.logger import get_logger
from app.features.points.model import Points
from app.features.partition.model import Partition
from .model import AIObjectsText
from .schema import AIObjectTextCreate, AIObjectTextUpdate,AIObjectTextDetail,AIObjectTextUpdatePoint

logger = get_logger(__name__)

class AIObjectsTextCRUD:
    """封裝對 AI_OBJECTS_TEXT 的 DB 操作"""

    # ───── Create ─────
    @staticmethod
    async def create(db: AsyncSession, data: AIObjectTextCreate) -> AIObjectsText:
        try:
            obj = AIObjectsText(**data.model_dump(exclude_none=True))
            db.add(obj)
            await db.flush()  # 拿到 PK
            logger.info(f"Create AI_OBJECTS_TEXT id={obj.ai_objectText_id}")
            await db.commit()
            await db.refresh(obj)
            return obj
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__AI_Object__point" in msg:
                detail = "無效的 point_id，該點位不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ───── Bulk list ─────
    @staticmethod
    async def get_all(db: AsyncSession) -> Sequence[AIObjectsText]:
        stmt = select(AIObjectsText).order_by(AIObjectsText.name)
        return (await db.scalars(stmt)).all()

    # ───── Joined detail (複雜 GET) ─────
    @staticmethod
    async def get_id(db: AsyncSession, ids: List[int]) -> List[Mapping[str, Any]]:
        """
        取得 AI_OBJECTS_TEXT 與關聯點位、分區資料：
        - 傳入逗號分隔的 ai_objectText_id 字串，可選；若 None 或空字串，回傳全部並依名稱排序
        - 回傳 List[AI
        ObjectsTextDetail]
        """
        stmt = (
            select(
                AIObjectsText.ai_objectText_id,
                AIObjectsText.name.label("ai_objectText_name"),
                AIObjectsText.font_family,
                AIObjectsText.font_style,
                AIObjectsText.font_size,
                AIObjectsText.text,
                AIObjectsText.font_color,
                AIObjectsText.point_id,
                Points.name.label("point_name"),
                Points.partition_id,
                Points.ai_id,
                Partition.name.label("partition_name"),
            )
            .join(Points, Points.point_id == AIObjectsText.point_id)
            .join(Partition, Points.partition_id == Partition.partition_id)
            .where(AIObjectsText.ai_objectText_id.in_(ids))
            .order_by(AIObjectsText.name)
        )

        result = await db.execute(stmt)
        rows = result.mappings().all()
        return [AIObjectTextDetail(**r) for r in rows]


    # ───── Update ─────
    @staticmethod
    async def update(db: AsyncSession, data: AIObjectTextUpdate) -> AIObjectsText:
        try:
            # 1) 先把 ORM instance 載入
            obj = await db.get(AIObjectsText, data.ai_objectText_id)
            if not obj:
                raise HTTPException(status_code=404, detail=f"ai_objectText_id={data.ai_objectText_id} 不存在")
            # 2) 把 payload 裡的欄位一一 assign
            update_data = data.model_dump(exclude_none=True, exclude={"ai_objectText_id"})
            for key, val in update_data.items():
                setattr(obj, key, val)
            # 3) commit 並 refresh，讓 obj 含最新資料
            await db.commit()
            await db.refresh(obj)
            return obj
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__AI_Object__point" in msg:
                detail = f"無效的 point_id = {data.point_id}，該點位不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
 
    @staticmethod
    async def update_point(db: AsyncSession, data: AIObjectTextUpdatePoint) -> AIObjectsText:
        """
        當Payload 只有兩欄位，也會更新
        {
            "ai_objectText_id": 786,
            "point_id": 52
        }
        """
        stmt = (
            update(AIObjectsText)
            .where(AIObjectsText.ai_objectText_id == data.ai_objectText_id)
            .values(point_id=data.point_id)
            .returning(AIObjectsText)                    
        )
        # 2. 執行
        result = await db.execute(stmt)
        row = result.scalar_one_or_none()                
        
        # 3. 找不到就 404
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AIObjectText id={data.ai_objectText_id} not found"
            )
        
        # 4. commit 後直接回傳 row（已經填入新的 point_id）
        await db.commit()
        return row

    # ───── Delete ─────
    @staticmethod
    async def delete(db: AsyncSession, oid: int) -> None:
        """刪除 AI_OBJECTS_TEXT 資料"""
        result = await db.execute(select(AIObjectsText.name, AIObjectsText.point_id)
                                  .where(AIObjectsText.ai_objectText_id == oid))
        row = result.one_or_none()
        
        if row is None:            
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"AI_OBJECTS_TEXT={oid} 不存在")
        
        _, point_id = row
        if point_id is not None:            
            point_name = await db.scalar(
                select(Points.name).where(Points.point_id == point_id)
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"已綁定點位 => {point_name or point_id}"
            )
        
        await db.execute(delete(AIObjectsText).where(AIObjectsText.ai_objectText_id == oid))
        await db.commit()

