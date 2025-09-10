from typing import List, Sequence, Mapping

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from fastapi import HTTPException, status
from .schema import SideUpdate
from .model import ViewsMenuSide                 # 你的主表
from app.features.views_menu_buttons.model import ViewsMenuButtons
from app.features.views.model import Views

class SideCrud:
    # ---------- READ ----------
    @staticmethod
    async def read_all(
        db: AsyncSession,
        *,
        menu_main_id: int | None = None,
        view_id: int | None = None,
        view_name: str | None = None,
        link_URL: str | None = None,
    ) -> Sequence[Mapping]:
        """
        回傳 JOIN 後的 dict list，直接餵給 Pydantic
        """
        
        # ① 先排出「樣式順位對照表」
        btn_order_cte = (
            select(
                ViewsMenuButtons.menu_buttons_id,
                # 1, 2, 3… 依 menu_buttons_id 遞增排序
                func.row_number()
                    .over(order_by=ViewsMenuButtons.menu_buttons_id)
                    .label("btn_pos")
            )
            .cte("btn_order")          # 做成 CTE 方便 JOIN
        )

        stmt = (
            select(
                ViewsMenuSide.menu_side_id,
                ViewsMenuSide.side_order,
                ViewsMenuSide.view_id,
                ViewsMenuSide.name,
                # ViewsMenuSide.menu_buttons_id,
                btn_order_cte.c.btn_pos.label("menu_buttons_id"), # 把順位當成 menu_buttons_id 回給前端
                ViewsMenuSide.menu_main_id,
                ViewsMenuSide.link_URL,
                # 按鈕
                ViewsMenuButtons.btn_height,
                ViewsMenuButtons.btn_width,
                ViewsMenuButtons.btn_textColor,
                ViewsMenuButtons.btn_text_FontSize,
                ViewsMenuButtons.btn_text_FontFamily,
                ViewsMenuButtons.btn_backgroundColor,
                # view
                Views.name.label("view_name"),
                Views.height.label("view_height"),
                Views.width.label("view_width"),
                Views.backgroundColor.label("view_backgroundColor"),
                Views.view_type.label("view_view_type"),
                Views.svg_tag.label("view_svg_tag"),
            )
            # 先把 Side 跟 Button 排名表連起來（不用怕重 JOIN，SQL Server 會優化）
            .join(btn_order_cte,
                ViewsMenuSide.menu_buttons_id == btn_order_cte.c.menu_buttons_id)
            .join(
                ViewsMenuButtons,
                ViewsMenuSide.menu_buttons_id == ViewsMenuButtons.menu_buttons_id,
            )
            .join(
                Views,
                ViewsMenuSide.view_id == Views.view_id,
                isouter=True,
            )
        )

        # 動態條件
        if menu_main_id is not None:
            stmt = stmt.where(ViewsMenuSide.menu_main_id == menu_main_id)
        if view_id is not None:
            stmt = stmt.where(ViewsMenuSide.view_id == view_id)
        if view_name is not None:
            stmt = stmt.where(Views.name.like(f"%{view_name}%"))
        if link_URL is not None:
            stmt = stmt.where(ViewsMenuSide.link_URL == link_URL)

        stmt = stmt.order_by(ViewsMenuSide.side_order)

        res = await db.execute(stmt)
        return res.mappings().all()

    # ---------- CREATE（批次） ----------
    
    @staticmethod
    async def create(db: AsyncSession, data: dict) -> int:
        # FIXME: 強制改數字 不妥 要綁 order 
        # 1. 用 offset 直接取「第 N 筆樣式」
        stmt_btn = (
            select(ViewsMenuButtons.menu_buttons_id)
            .order_by(ViewsMenuButtons.menu_buttons_id)
            .offset(data.menu_buttons_id - 1)    # 使用者從 1 開始輸入
            .limit(1)
        )
        menu_btn_id = (await db.execute(stmt_btn)).scalar_one_or_none()
        if menu_btn_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="按鈕樣式不存在或序號超出範圍",
            )

        # 2. 把真正的 FK 寫回 data
        data.menu_buttons_id = menu_btn_id

        stmt = (
            insert(ViewsMenuSide)
            .values(**data.model_dump(exclude_none=True))
            .returning(ViewsMenuSide.menu_side_id)
        )
        try:
            menu_side_id = (await db.execute(stmt)).scalar_one()
            await db.commit()
            return menu_side_id  
        
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
        
    # ---------- UPDATE ----------
    @staticmethod
    async def update_one(db: AsyncSession, payload:SideUpdate) -> Mapping | None:
        try:            
            # 1. 用 offset 直接取「第 N 筆樣式」
            stmt_btn = (
                select(ViewsMenuButtons.menu_buttons_id)
                .order_by(ViewsMenuButtons.menu_buttons_id)
                .offset(payload.menu_buttons_id - 1)    # 使用者從 1 開始輸入
                .limit(1)
            )
            real_btn_id = (await db.execute(stmt_btn)).scalar_one_or_none()
            if real_btn_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="按鈕樣式不存在或序號超出範圍",
                )

            # 2. 把真正的 FK 寫回 data
            
            menu_side_id = payload.menu_side_id
            update_values = payload.model_dump(
                exclude={"menu_side_id", "menu_buttons_id"},
                exclude_none=True,
            )
            update_values["menu_buttons_id"] = real_btn_id

            result = await db.execute(
                update(ViewsMenuSide)
                .where(ViewsMenuSide.menu_side_id == menu_side_id)
                .values(**update_values)
                .returning(*ViewsMenuSide.__table__.c)
            )
            row = result.first()
            await db.commit()

            # 3) 轉成 dict，再把 menu_buttons_id 換回「序號」
            result = dict(row._mapping)
            result["menu_buttons_id"] = payload.menu_buttons_id
            return result

            # # 取更新後 JOIN 資料再回傳
            # rows = await SideCrud.read_all(db, menu_main_id=None, view_id=None, view_name=None, link_URL=None)
            # for r in rows:
            #     if r["menu_side_id"] == menu_side_id:
            #         return r
            # return None
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__VIEWS_MEN__menu___3C34F16F" in msg:
                detail = "無效的 menu_buttons_id，該按鈕樣式不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
        
    # ---------- DELETE ----------
    @staticmethod
    async def delete_one(db: AsyncSession, menu_side_id: int) ->  None:
        stmt = (
            delete(ViewsMenuSide)
            .where(ViewsMenuSide.menu_side_id == menu_side_id)
        )
        await db.execute(stmt)
        await db.commit()
