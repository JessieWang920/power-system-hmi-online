# backend/app/features/views_menu_main/crud.py
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.logger import get_logger
from .model import ViewsMenuMain
from app.features.views.model            import Views
from app.features.views_menu_buttons.model import ViewsMenuButtons  

logger = get_logger(__name__)

class MenuMainCRUD:

    # ── 新增 ───────────────────
    @staticmethod
    async def create(db: AsyncSession, data):
        try:
            stmt = (
                insert(ViewsMenuMain)
                .values(**data.model_dump(exclude_none=True))
                .returning(ViewsMenuMain.menu_main_id)
            )
            mid = (await db.execute(stmt)).scalar_one()
            await db.commit()
            return mid
        except IntegrityError as e:
                await db.rollback()
                raw = getattr(e, "orig", None)
                msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
                if "FK__VIEWS_MAI__view" in msg:
                    detail = "無效的 view_id，該圖面不存在。"
                elif "FK__VIEWS_MEN__menu" in msg:
                    detail = "無效的 menu_buttons_id，該按鈕不存在。"
                else:
                    detail = f"更新失敗：{msg}"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ── 更新 ───────────────────
    @staticmethod
    async def update(db: AsyncSession, data):
        try:
            stmt = (
                update(ViewsMenuMain)
                .where(ViewsMenuMain.menu_main_id == data.menu_main_id)
                .values(**data.model_dump(exclude={"menu_main_id"}, exclude_none=True))
                .returning(ViewsMenuMain)
            )
            row = (await db.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise HTTPException(status_code=404, detail="menu_main_id 不存在")
            await db.commit()
            return row
        except IntegrityError as e:
                await db.rollback()
                raw = getattr(e, "orig", None)
                msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
                if "FK__VIEWS_MAI__view" in msg:
                    detail = "無效的 view_id，該圖面不存在。"
                elif "FK__VIEWS_MEN__menu" in msg:
                    detail = "無效的 menu_buttons_id，該按鈕不存在。"
                else:
                    detail = f"更新失敗：{msg}"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ── 刪除 ───────────────────
    @staticmethod
    async def delete(db: AsyncSession, mid: int) -> None:
        stmt = (
            delete(ViewsMenuMain)
            .where(ViewsMenuMain.menu_main_id == mid)
        )
        await db.execute(stmt)
        await db.commit()

    # ── 查詢（含 join 欄位）────
    @staticmethod
    async def list(db: AsyncSession) -> list[dict]:
        stmt = (
            select(
                ViewsMenuMain.menu_main_id,
                ViewsMenuMain.main_order,
                ViewsMenuMain.view_id,
                ViewsMenuMain.name,
                ViewsMenuMain.menu_buttons_id,
                ViewsMenuMain.link_URL,
                ViewsMenuMain.isMain,
                ViewsMenuButtons.btn_height,
                ViewsMenuButtons.btn_width,
                ViewsMenuButtons.btn_textColor,
                ViewsMenuButtons.btn_text_FontSize,
                ViewsMenuButtons.btn_text_FontFamily,
                ViewsMenuButtons.btn_backgroundColor,
                Views.name.label("view_name"),
                Views.height.label("view_height"),
                Views.width.label("view_width"),
                Views.backgroundColor.label("view_backgroundColor"),
                Views.view_type.label("view_view_type"),
                Views.svg_tag.label("view_svg_tag"),
            )
            .join(ViewsMenuButtons, ViewsMenuMain.menu_buttons_id == ViewsMenuButtons.menu_buttons_id)
            .join(Views,          ViewsMenuMain.view_id         == Views.view_id)
            .order_by(ViewsMenuMain.menu_main_id)
        )
        result = await db.execute(stmt)
        rows = result.all()
        # 每一列 Row._mapping 就是 dict，直接回傳給 FastAPI
        return [ dict(r._mapping) for r in rows ]
    
