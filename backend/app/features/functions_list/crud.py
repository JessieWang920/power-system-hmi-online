# backend/app/features/functions_list/crud.py
from sqlalchemy import select, insert, update, delete,text
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.logger import get_logger
from .model import FunctionsList
from .schema import FunctionCreate, FunctionUpdate
from app.features.functions_formula.model import  FunctionsFormula
from app.features.functions_operator.model import   FunctionsOperator

logger = get_logger(__name__)

class FunctionCRUD:

    # ── 建立 ──────────────────────────────────────────
    @staticmethod
    async def create(db: AsyncSession, data: FunctionCreate) -> FunctionsList:
        stmt = (
            insert(FunctionsList)
            .values(name=data.function_name.strip(), parameters=data.parameters)
            .returning(FunctionsList)
        )
        row = (await db.execute(stmt)).scalar_one()
        await db.commit()
        return row

    # ── 更新 ──────────────────────────────────────────
    @staticmethod
    async def update(db: AsyncSession, data: FunctionUpdate) -> FunctionsList:
        stmt = (
            update(FunctionsList)
            .where(FunctionsList.function_id == data.function_id)
            .values(name=data.function_name.strip(), parameters=data.parameters)
            .returning(FunctionsList)
        )
        row = (await db.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="function_id 不存在")
        await db.commit()
        return row

    # ── 刪除 ──────────────────────────────────────────
    @staticmethod
    async def delete(db: AsyncSession, fid: int) -> FunctionsList:
        await db.execute(delete(FunctionsFormula).where(FunctionsFormula.function_id == fid))
        await db.execute(delete(FunctionsList).where(FunctionsList.function_id == fid))   
        await db.commit()

    # ── 取得全部 ──────────────────────────────────────
    @staticmethod
    async def get_all(db: AsyncSession):
        rows = (await db.execute(select(FunctionsList))).scalars().all()
        return rows

    # ── 取得單筆（含 sub）───────────────────────────────
    @staticmethod
    async def get_id(db: AsyncSession, fid: int):
        op = aliased(FunctionsOperator)
        stmt = (
            select(
                FunctionsList,
                FunctionsFormula,
                op.name.label("fu_operator_name")
            )
            .join(FunctionsFormula, FunctionsFormula.function_id == FunctionsList.function_id, isouter=True)
            .join(op, op.fu_operator_id == FunctionsFormula.fu_operator_id, isouter=True)
            .where(FunctionsList.function_id == fid)
            .order_by(FunctionsFormula.formula_order)
        )
        rows = (await db.execute(stmt)).mappings().all()
        # rows = (await db.execute(stmt)).all()
        if not rows:
            return None

        base = rows[0]["FunctionsList"]     # 只會有一筆
        sub = [
            {
                **rows[i]['FunctionsFormula'].__dict__,  # 或使用 Pydantic model_dump
                "fu_operator_name": rows[i]['fu_operator_name']
            }
            for i in range(len(rows))
            if rows[i]['FunctionsFormula'] is not None
        ]
        return base, sub