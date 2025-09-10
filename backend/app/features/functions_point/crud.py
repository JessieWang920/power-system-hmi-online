# backend/app/features/functions_point/crud.py
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from fastapi import HTTPException, status

from app.core.logger import get_logger
from .model import FunctionsPoints
from app.features.functions_formula.model import FunctionsFormula
from app.features.functions_list.model    import FunctionsList
from app.features.points.model            import Points
from app.features.partition.model         import Partition

logger = get_logger(__name__)


class FPCRUD:
    # ─────────────────────────────────── 新增 ────────────────────────────────────
    @staticmethod
    async def create(db: AsyncSession, data):
        stmt = (
            insert(FunctionsPoints)
            .values(**data.model_dump(exclude_none=True))
            .returning(FunctionsPoints.fu_point_id)
        )
        try:
            fu_point_id = (await db.execute(stmt)).scalar_one()
            await db.commit()
            return fu_point_id
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"新增失敗：{e}") from e

    # ─────────────────────────────────── 查詢 ────────────────────────────────────
    @staticmethod
    async def read_by_sdi(db: AsyncSession, sdi_id: int | None):
        """
        依 SDI_ID 取得所有對應資料  
        - 若 sdi_id 為 None，直接回傳空陣列（符合前端傳 null 的情境）  
        """
        if sdi_id is None:
            return []

        P1 = aliased(Points)      # SDI 點
        P2 = aliased(Points)      # Point (AI/DI)
        PA1 = aliased(Partition)
        PA2 = aliased(Partition)

        stmt = (
            select(
                FunctionsPoints.fu_point_id,
                FunctionsPoints.sdi_id.label("fu_sdi_id"),
                FunctionsFormula.formula_order,
                FunctionsList.function_id,
                FunctionsList.name.label("function_name"),

                P1.name.label("fu_sdi_point_name"),
                P1.partition_id.label("fu_sdi_partition_id"),
                PA1.name.label("fu_sdi_partition_name"),

                P2.point_id.label("fu_point_point_id"),
                P2.name.label("fu_point_point_name"),
                P2.partition_id.label("fu_point_partition_id"),
                PA2.name.label("fu_point_partition_name"),
                P2.ai_id.label("fu_point_ai_id"),
                P2.di_id.label("fu_point_di_id"),
            )
            .join(FunctionsFormula, FunctionsFormula.fu_formula_id == FunctionsPoints.fu_formula_id, isouter=True)
            .join(FunctionsList, FunctionsList.function_id == FunctionsFormula.function_id, isouter=True)
            .join(P1, P1.sdi_id == FunctionsPoints.sdi_id, isouter=True)
            .join(PA1, PA1.partition_id == P1.partition_id, isouter=True)
            .join(P2, P2.point_id == FunctionsPoints.point_id, isouter=True)
            .join(PA2, PA2.partition_id == P2.partition_id, isouter=True)
            .where(FunctionsPoints.sdi_id == sdi_id)
            .order_by(FunctionsFormula.formula_order)
        )
        result = await db.execute(stmt)
        return result.mappings().all()

    # @staticmethod
    # async def read_by_sdi(db: AsyncSession, sdi_id: int) -> list[dict]:
    #     # 先替 Points / Partition 做別名，避免同一張表被 join 兩次時名稱衝突
    #     P1  = aliased(Points)
    #     P2  = aliased(Points)
    #     PA1 = aliased(Partition)
    #     PA2 = aliased(Partition)

    #     stmt = (
    #         select(
    #             FunctionsPoints.fu_point_id,
    #             FunctionsPoints.sdi_id.label("fu_sdi_id"),
    #             FunctionsFormula.formula_order,
    #             FunctionsList.function_id,
    #             FunctionsList.name.label("function_name"),
    #             #
    #             P1.name.label("fu_sdi_point_name"),
    #             P1.partition_id.label("fu_sdi_partition_id"),
    #             PA1.name.label("fu_sdi_partition_name"),
    #             #
    #             P2.point_id.label("fu_point_point_id"),
    #             P2.name.label("fu_point_point_name"),
    #             P2.partition_id.label("fu_point_partition_id"),
    #             PA2.name.label("fu_point_partition_name"),
    #             P2.ai_id.label("fu_point_ai_id"),
    #             P2.di_id.label("fu_point_di_id"),
    #         )
    #         .select_from(FunctionsPoints)
    #         .outerjoin(FunctionsFormula,
    #                    FunctionsFormula.fu_formula_id == FunctionsPoints.fu_formula_id)
    #         .outerjoin(FunctionsList,
    #                    FunctionsList.function_id == FunctionsFormula.function_id)
    #         .outerjoin(P1,  P1.sdi_id      == FunctionsPoints.sdi_id)
    #         .outerjoin(PA1, PA1.partition_id == P1.partition_id)
    #         .outerjoin(P2,  P2.point_id    == FunctionsPoints.point_id)
    #         .outerjoin(PA2, PA2.partition_id == P2.partition_id)
    #         .where(FunctionsPoints.sdi_id == sdi_id)
    #         .order_by(FunctionsFormula.formula_order)
    #     )

    #     rows = (await db.execute(stmt)).mappings().all()
    #     return [dict(r) for r in rows]

    # ─────────────────────────────────── 更新 ────────────────────────────────────
    @staticmethod
    async def update(db: AsyncSession, data):
        stmt = (
            update(FunctionsPoints)
            .where(FunctionsPoints.fu_point_id == data.fu_point_id)
            .values(**data.model_dump(exclude={"fu_point_id"}))
            .returning(FunctionsPoints.fu_point_id)
        )
        res = (await db.execute(stmt)).scalar_one_or_none()
        if res is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="fu_point_id 不存在")
        await db.commit()
        return res

    # ─────────────────────────────────── 刪除 ────────────────────────────────────
    @staticmethod
    async def delete(db: AsyncSession, fu_point_id: int) -> dict:
        stmt = (
            delete(FunctionsPoints)
            .where(FunctionsPoints.fu_point_id == fu_point_id)
            .returning(
                FunctionsPoints.fu_point_id,
                FunctionsPoints.point_id,
                FunctionsPoints.fu_formula_id,
                FunctionsPoints.sdi_id,
            )
        )
        row = (await db.execute(stmt)).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="fu_point_id 不存在")
        await db.commit()
        return dict(row)
