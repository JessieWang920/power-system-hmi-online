# backend/app/features/views/crud.py
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.logger import get_logger
from app.features.view_shapes.model import ViewShape
from .model import Views
from typing import List, Mapping, Any

logger = get_logger(__name__)

class ViewCRUD:
    # ---------- 建立 ----------
    @staticmethod
    async def create(db: AsyncSession, data) -> Views:
        stmt = (
            insert(Views)
            .values(**data.model_dump(exclude_none=True))
            .returning(Views)
        )
        row = (await db.execute(stmt)).scalar_one()
        await db.commit()
        return row

    # ---------- 讀取 ----------
    @staticmethod
    async def get_all(db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(Views))).scalars().all()
        return [r.__dict__ for r in rows]

    @staticmethod
    async def get_id(db: AsyncSession, vid: int) -> Views | None:
        row = (await db.execute(select(Views).where(Views.view_id == vid))).scalar_one_or_none()
        return row

    # ---------- 更新 ----------
    @staticmethod
    async def update(db: AsyncSession, data) -> Views:
        stmt = (
            update(Views)
            .where(Views.view_id == data.view_id)
            .values(**data.model_dump(exclude={"view_id"}))
            .returning(Views)
        )
        row = (await db.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="view_id 不存在")
        await db.commit()
        return row

    # ---------- 刪除 ----------
    @staticmethod
    async def delete(db: AsyncSession, vid: int) -> None:
        row = await ViewCRUD.get_id(db, vid)
        if row is None:
            raise HTTPException(status_code=404, detail=f"view_id 不存在")
        
        await db.execute(delete(ViewShape).where(ViewShape.view_id == vid))      
        await db.execute(delete(Views).where(Views.view_id == vid))
        await db.commit()

