from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import MqttHmiMx
from app.core.logger import get_logger
from typing import  Mapping

logger = get_logger(__name__)

class MqttMxCrud:

    # ── 查詢 ────────────────────────────────────────
    @staticmethod
    async def read_all(db: AsyncSession, limit: int = 5000) -> list[Mapping]:
        stmt = select(model := MqttHmiMx)#.order_by(model.time.desc()).limit(limit)
        return (await db.execute(stmt)).scalars().all()
    