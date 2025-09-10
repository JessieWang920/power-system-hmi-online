from sqlalchemy import select
from .model import  MqttHmiSt
from typing import  Mapping
from sqlalchemy.ext.asyncio import AsyncSession


class MqttStCrud:
    # ── 查詢 ────────────────────────────────────────
    @staticmethod
    async def read_all(db: AsyncSession, limit: int = 5000) -> list[Mapping]:
        stmt = select(model := MqttHmiSt)#.order_by(model.time.desc()).limit(limit)
        return (await db.execute(stmt)).scalars().all()
    
    