from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.core.logger import get_logger
from .model import ElementsShapes

log = get_logger(__name__)

class ShapeCRUD:
    @staticmethod
    async def create(db: AsyncSession, data) -> list[ElementsShapes]:
        try:
            rows = [data] if not isinstance(data, list) else data
            stmt = (
                insert(ElementsShapes)
                .values([r.model_dump(exclude_none=True,exclude={"shape_name"}) for r in rows])  # type: ignore
                .returning(ElementsShapes)
            )
            result = (await db.execute(stmt)).scalars().all()
            await db.commit()
            return result
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__ELEMENTS___elem" in msg:
                detail = "無效的 elem_id，該元素不存在。"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
        except Exception as e:
            log.error(f"ElementsShapes create error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建失败")

    @staticmethod
    async def update(db: AsyncSession, data):
        try:
            stmt = (
                update(ElementsShapes)
                .where(ElementsShapes.elem_shapes_id == data.elem_shapes_id)
                .values(**data.model_dump(exclude={"elem_shapes_id","shape_name"}))
                .returning(ElementsShapes)
            )
            row = (await db.execute(stmt)).scalar_one_or_none()
            if not row:
                raise HTTPException(status_code=404, detail="elem_shapes_id 不存在")
            await db.commit()
            return row
        except IntegrityError as e:
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__ELEMENTS___shape" in msg:
                detail = "無效的 shape_name_id，該樣式不存在。"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="elemen_shapes 更新失敗")


    @staticmethod
    async def delete(db: AsyncSession, sid: int):

        # 如果根本沒這筆 id，直接回 404
        result = await db.execute(select(ElementsShapes.elem_id).where(ElementsShapes.elem_shapes_id == sid))
        row = result.one_or_none()
        if row is None:            
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"elem_shapes_id={sid} 不存在")
        


        await db.execute(delete(ElementsShapes).where(ElementsShapes.elem_shapes_id == sid))
        await db.commit()
