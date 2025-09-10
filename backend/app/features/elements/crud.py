# backend/app/features/elements/crud.py
from sqlalchemy import select, insert, update, delete,  join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.core.logger import get_logger
from .model import Elements

from app.features.shapes_name.model     import ShapesName
from app.features.elements_shapes.model import ElementsShapes
from app.features.points.model          import Points
from app.features.elements.schema       import  ElementShape,ElementResp,ElementBinding
from app.features.view_shapes.model     import ViewShape
from app.features.views.model           import Views

logger = get_logger(__name__)

class ElementCRUD:
    # ── 建立 ──────────────────────────────────────────
    @staticmethod
    async def create(db: AsyncSession, data) -> Elements:
        try:
            # 未使用到 disabled、view_name，所以先 exclude 掉
            stmt = (
                insert(Elements)
                .values(**data.model_dump(exclude_none=True,exclude={"disabled","view_name"}))
                .returning(Elements)
            )
        
            row = (await db.execute(stmt)).scalar_one()
            await db.commit()
            return row
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__ELEMENTS__point" in msg:
                detail = "無效的 point_id，該點位不存在。"
            elif "FK__ELEMENTS__view_i" in msg:
                detail = "無效的 view_id，該視圖不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ── 更新 ──────────────────────────────────────────
    @staticmethod
    async def update_view( db: AsyncSession, data: ElementBinding) -> Elements:
        stmt = (
            update(Elements).where(Elements.elem_id == data.elem_id).values(view_id=data.view_id)
            .returning(Elements)
        )
        try:
            result = await db.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"elem_id={data.elem_id} 不存在，無法更新 view_id。"
                )
            await db.commit()
            return row
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error binding parameter view: {e}"
            )


    @staticmethod
    async def update(db: AsyncSession, data) -> Elements:
        try:
            # 更新資料庫，回傳elem_id
            stmt = (
                update(Elements)
                .where(Elements.elem_id == data.elem_id)
                # .values(**data.model_dump(exclude={"elem_id","disabled"}))
                .values(**data.model_dump(exclude={"elem_id", "disabled", "point_name", "view_name"}))
                .returning(Elements.elem_id)
            )
            
            elem_id  = (await db.execute(stmt)).scalar_one_or_none()
            if elem_id  is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="elem_id 不存在")
            await db.commit()

            sel_stmt = (
                select(
                    *Elements.__table__.c,
                    Points.name.label("point_name")
                )
                .select_from(Elements)
                .outerjoin(Points, Points.point_id == Elements.point_id)
                .where(Elements.elem_id == elem_id)
            )
            row = (await db.execute(sel_stmt)).mappings().one()
            return ElementResp(**row)

        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__ELEMENTS__point" in msg:
                detail = "無效的 point_id，該點位不存在。"
            elif "FK__ELEMENTS__view_i" in msg:
                detail = "無效的 view_id，該視圖不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ── 刪除（含參照檢查）──────────────────────────────
    @staticmethod
    async def delete(db: AsyncSession, eid: int) ->  None:
        # ViewShape 若有視窗綁定直接 raise
        view_ref = await db.scalar(
            select(ViewShape.view_shape_id)   # 只抓一筆就夠判斷
            .where(ViewShape.elem_id == eid)
            .limit(1)
        )
        if view_ref is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f" 圖面清單(ViewShape) 已綁定 elem_id={eid}"
            )

        # 確認 Element tb 的 view_id / point_id 無綁定
        result = await db.execute(
            select(Elements.view_id, Elements.point_id)
            .where(Elements.elem_id == eid)
        )
        row = result.one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"elem_id={eid} 不存在"
            )

        # 任一欄位  view_id, point_id 有值，代表被綁定，raise
        view_id, point_id = row        
        msg_parts: list[str] = []
        
        # 取出點位/視窗名稱，若查不到就顯示 id
        if view_id is not None:
            view_name = await db.scalar(
                select(Views.name).where(Views.view_id == view_id)
            )
            msg_parts.append(f"視窗 => {view_name or view_id}")
        if point_id is not None:            
            point_name = await db.scalar(
                select(Points.name).where(Points.point_id == point_id)
            )
            msg_parts.append(
                f"點位 => {point_name or point_id}"
            )

        if msg_parts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已綁定" + " / ".join(msg_parts)
            )
        
        # 確定可刪除 element 後，ELEMENTS_SHAPES tb 若有符合 elem_id 則一併刪除
        await db.execute(delete(ElementsShapes).where(ElementsShapes.elem_id == eid))    
        await db.execute(delete(Elements).where(Elements.elem_id == eid))
        await db.commit()


    

    # @staticmethod
    # async def delete(db: AsyncSession, eid: int) ->  tuple[int | None, int | None]:
    #     sel1 = select(ElementsShapes.elem_shapes_id.label("id")).where(ElementsShapes.elem_id == eid)
    #     sel2 = select(ViewShape.view_shape_id.label("id")).where(ViewShape.elem_id == eid)
    #     refs = (await db.execute(union_all(sel1, sel2))).scalars().all()
    #     if refs:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"刪除失敗：仍被 狀態清單(ELEMENTS_SHAPES) / 圖面清單(VIEW_SHAPES) 綁定 {refs}"
    #         )
        
    #     # 如果根本沒這筆 element，直接回 404
    #     result = await db.execute(select(Elements.view_id, Elements.point_id).where(Elements.elem_id == eid))
    #     row = result.one_or_none()
    #     if row is None:            
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail=f"elem_id={eid} 不存在")
        
    #     await db.execute(delete(Elements).where(Elements.elem_id == eid))
    #     await db.commit()

    #     # 目前只回傳 告知有綁定 point 及 view 的資訊。
    #     view_id, point_id = row
    #     return view_id, point_id
    
        # 綁定 point 及 view 的狀態下 要再次詢問是否刪除
        # view_id, point_id = row
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail=(
        #         f"刪除前請注意：elem_id={eid} 目前綁定 view_id={view_id}、point_id={point_id}。"
        #         " 確定要刪除嗎？"
        #     )
        # )
        # 前端傳入 force=true 才可刪除
        # if force:
        #     await db.execute(delete(Elements).where(Elements.elem_id == eid))
        #     await db.commit()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[dict]:
        # 把 ELEMENTS 跟 VIEWS left join 起來
        j = (
            join(Elements, Views,  Elements.view_id  == Views.view_id,  isouter=True)
            .join(Points,   Elements.point_id == Points.point_id, isouter=True)
        )

        # SELECT 欄位並做 alias
        stmt = (
            select(
                Elements.elem_id,
                Elements.point_id,
                Points.name.label("point_name"), 
                Elements.name.label("elem_name"),
                Elements.link_URL,
                Elements.view_id,
                Views.name.label("view_name"),
                Elements.isLock
            )
            .select_from(j)
        )
        # mappings() 拿到 dict 而不是 ORM 實例
        rows = (await db.execute(stmt)).mappings().all()
        return [dict(r) for r in rows]    

    # # ── 詳細（含 sub）──────────────────────────────────
    @staticmethod
    async def get_id(db: AsyncSession, eid: int) -> list[dict]:
        # 1) 把所有扁平化的 rows 撈出來
        j = (
            join(Elements, Views, Elements.view_id == Views.view_id, isouter=True)
            .join(ElementsShapes, Elements.elem_id == ElementsShapes.elem_id, isouter=True)
            .join(ShapesName, ElementsShapes.shape_name_id == ShapesName.shape_name_id, isouter=True)
            .join(Points,Elements.point_id == Points.point_id,isouter=True)
        )
        stmt = (
            select(
                Elements.elem_id,
                Elements.point_id,
                Points.name.label("point_name"),        # ★ 取出點位名稱
                Elements.name,
                Elements.view_id,
                Elements.link_URL,
                Elements.isLock,
                Views.name.label("view_name"),
                ElementsShapes.elem_shapes_id,
                ElementsShapes.status,
                ElementsShapes.statu_default,
                ElementsShapes.shape_name_id,
                ShapesName.name.label("shape_name"),
            )
            .select_from(j)
            .where(Elements.elem_id == eid)
            .order_by(ElementsShapes.elem_shapes_id)
        )
        
        result = await db.execute(stmt)
        rows = result.mappings().all()
        if not rows:
            return []        
        # 自動取得 sub schema 的欄位名稱（ElementShape）
        sub_keys = set(ElementShape.model_fields.keys())
        # 主資料只留下非 sub 欄位
        first = rows[0]
        base_data = {k: v for k, v in first.items() if k not in sub_keys}
        # sub list 用 ElementShape 解析
        base_data["sub"] = [
            ElementShape(**{k: v for k, v in r.items() if k in sub_keys}) 
            for r in rows 
            if r["elem_shapes_id"] is not None 
            ]

        return base_data
