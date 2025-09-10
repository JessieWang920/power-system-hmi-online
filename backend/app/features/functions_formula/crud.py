# backend/app/features/functions_formula/crud.py
from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.core.logger import get_logger
from .model import FunctionsFormula
from .schema import FFCreate, FFUpdate

logger = get_logger(__name__)

class FFCRUD:

    # ── 建立 ─────────────────────────
    @staticmethod
    async def create(db: AsyncSession, data: FFCreate) -> FunctionsFormula:
        stmt = (
            insert(FunctionsFormula)
            .values(**data.model_dump(exclude_none=True))
            .returning(FunctionsFormula)
        )
        try:
            row = (await db.execute(stmt)).scalar_one()
            await db.commit()
            return row
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__FUNCTIONS__fu_op__6C190EBB" in msg:
                detail = "無效的 fu_operator_id，該公式運算子不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ── 更新 ─────────────────────────
    @staticmethod
    async def update(db: AsyncSession, data: FFUpdate) -> FunctionsFormula:
        stmt = (
            update(FunctionsFormula)
            .where(FunctionsFormula.fu_formula_id == data.fu_formula_id)
            .values(**data.model_dump(exclude={"fu_formula_id"}, exclude_none=True))
            .returning(FunctionsFormula)
        )
        row = (await db.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fu_formula_id 不存在")
        await db.commit()
        return row

    # ── 刪除 ─────────────────────────
    @staticmethod
    async def delete(db: AsyncSession, fid: int) -> FunctionsFormula:
        try:
            stmt = (
                delete(FunctionsFormula)
                .where(FunctionsFormula.fu_formula_id == fid)
                .returning(FunctionsFormula)
            )
            row = (await db.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fu_formula_id 不存在")
            await db.commit()
            return row
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__FUNCTIONS__fu_fo__" in msg:
                detail = "已有綁定的公式參數點位置。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
        
    # ── 其它查詢（示範給 MQTT 批次用）────────
    @staticmethod
    async def bulk_insert(db: AsyncSession, rows: list[dict]) -> None:
        """
        rows: List[dict] 其 key 必須與資料表欄位一致。
        使用 transaction + executemany 批次寫入，提高效能。
        """
        if not rows:
            return
        await db.execute(insert(FunctionsFormula), rows)
        await db.commit()
