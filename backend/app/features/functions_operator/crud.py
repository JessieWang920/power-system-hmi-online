# backend/app/features/functions_operator/crud.py
from typing import List, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import get_logger
from .model import FunctionsOperator

logger = get_logger(__name__)
class FOCrud:
    @staticmethod
    async def read_all(db: AsyncSession) -> List[FunctionsOperator]:
        stmt = select(FunctionsOperator)
        result: Sequence[FunctionsOperator] = (await db.scalars(stmt)).all()
        return result

    @staticmethod
    async def read_by_id(db: AsyncSession, fo_id: int) -> FunctionsOperator | None:
        result = await db.get(FunctionsOperator, fo_id)
        return result
