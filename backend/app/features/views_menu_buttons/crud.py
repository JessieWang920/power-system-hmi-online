# backend/app/features/views_menu_buttons/crud.py
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.core.logger import get_logger
from .model import ViewsMenuButtons
from .schema import VMBCreate, VMBUpdate

logger = get_logger(__name__)

class VMBCRUD:
    # ── 建立 ─────────────────
    @staticmethod
    async def create(db: AsyncSession, data: VMBCreate) -> ViewsMenuButtons:
        stmt = insert(ViewsMenuButtons).values(**data.model_dump()).returning(ViewsMenuButtons)
        row = (await db.execute(stmt)).scalar_one()
        await db.commit()
        return row

    # ── 查詢 all / by id ─────
    @staticmethod
    async def read(db: AsyncSession, vid: int | None = None):
        stmt = select(ViewsMenuButtons)
        if vid is not None:
            stmt = stmt.where(ViewsMenuButtons.menu_buttons_id == vid)
        result = await db.execute(stmt)
        return result.scalars().all()

    # ── 更新 ─────────────────
    @staticmethod
    async def update(db: AsyncSession, data: VMBUpdate):
        stmt = (
            update(ViewsMenuButtons)
            .where(ViewsMenuButtons.menu_buttons_id == data.menu_buttons_id)
            .values(**data.model_dump(exclude={"menu_buttons_id"}))
            .returning(ViewsMenuButtons)
        )
        row = (await db.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="menu_buttons_id 不存在")
        await db.commit()
        return row

    # ── 刪除 ─────────────────
    @staticmethod
    async def delete(db: AsyncSession, mid: int):
        try:
            stmt = delete(ViewsMenuButtons).where(ViewsMenuButtons.menu_buttons_id == mid)
            await db.execute(stmt)
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__VIEWS_MEN__menu" in msg:
                detail = "該按鈕被使用中"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e