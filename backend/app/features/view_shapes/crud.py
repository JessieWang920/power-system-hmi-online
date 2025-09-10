# backend/app/features/view_shapes/crud.py
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.core.logger import get_logger
from .model import ViewShape
from .schema import VSCreate, VSUpdate, VSResp

log = get_logger(__name__)

class VSCRUD:
    # ── 建立─────────────────────────────────────
    @staticmethod
    async def create(db:AsyncSession, data:VSCreate) -> list[VSResp]:
        """
        前端傳入會根據 obj、shape、element 有不一樣格式的 payload，
        最終都會轉成這個 VSCreate schema
        """
        # 統一留下真正要寫 DB 的七欄
        allowed = {                
            "view_shape_order", "x", "y", "view_id",
            "shape_name_id", "elem_id", "ai_objectText_id"
            }
        values = data.model_dump(include=allowed)
        stmt = insert(ViewShape).values(values).returning(ViewShape)
        try:
            result = (await db.execute(stmt)).scalar_one()
            await db.commit()
            return result
            # return [VSResp.model_validate(r) for r in result.scalars()]
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__VIEW_SHAP__view___29AC2CE0" in msg:
                detail = f"無效的 view_id = {values.get('view_id')}，該視圖不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ── 批次更新──────────────────────────────────────
    @staticmethod
    async def update(db:AsyncSession, data:list[VSUpdate]) -> list[VSResp]:
        """
        會因為刪除觸發編輯，把所有層級照順序重排
        只能更改位置 x、y、層級，無法更改綁定項目
        """
        updated: list[VSResp] = []
        for rec in data:
            stmt = (update(ViewShape)
                    .where(ViewShape.view_shape_id == rec.view_shape_id)
                    .values(rec.model_dump(exclude={"view_shape_id"}))
                    .returning(ViewShape))
            row = (await db.execute(stmt)).scalar_one_or_none()
            if not row:
                raise HTTPException(status_code=404,
                                    detail=f"view_shape_id={rec.view_shape_id} 不存在")
            updated.append(VSResp.model_validate(row))
        await db.commit()
        return updated

    # ── 刪除─────────────────────────────────────────
    @staticmethod
    async def delete(db:AsyncSession, vid:int) -> None:
        stmt = delete(ViewShape).where(ViewShape.view_shape_id == vid)
        result = await db.execute(stmt)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"view_shape_id={vid} 不存在")
