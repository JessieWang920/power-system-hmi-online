# backend/app/features/shapes_name/crud.py
from sqlalchemy import select, insert, update, delete, join, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from .model import ShapesName
from .schema import ShapeNameCreate, ShapeNameUpdate,ShapeNameResp, ShapeNameUpdateBinding
from app.features.views.model import Views
from app.features.shapes.model import Shapes
from app.features.elements_shapes.model import ElementsShapes
from app.features.view_shapes.model import ViewShape

from app.core.logger import get_logger
from app.core.config import settings

from pathlib import Path
import base64
import os, json

logger = get_logger(__name__)
# IMG_DIR = Path(settings().image_dir)
cfg = settings()

class ShapeNameCRUD:

    @staticmethod
    async def create(db: AsyncSession, data: ShapeNameCreate) -> ShapesName:
        stmt = (
            insert(ShapesName)
            # 暫時不要帶 group_x
            # .values(**data.model_dump(exclude={"svgObjects"}))
            .values(**data.model_dump(exclude={"svgObjects", "group_x"}))            
            .returning(ShapesName)
        )
        row = (await db.execute(stmt)).scalar_one()
        await db.commit()
        return row
    
    @staticmethod
    async def create_pic(data: ShapeNameCreate):
        """
        將 svg 原始碼或 base64 data url 存成檔案，
        寫失敗就丟 HTTPException
        """        
        # file_path = IMG_DIR / data.name
        file_path = cfg.image_dir/data.name
        fn = data.name.lower()
        try:
            if fn.endswith(".svg"):
                # svg 存文字檔
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(data.svgObjects)

            elif fn.endswith(".png"):
                # split header, 再 decode
                try:
                    _, b64 = data.svgObjects.split(",", 1)
                except ValueError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST 
                                        , detail="Invalid PNG data URL")     
        
                img_data = base64.b64decode(b64)
                with open(file_path, "wb") as f:
                    f.write(img_data)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST 
                                        , detail=f"確認副檔名，非.svg、.png 檔案: {data.name}") 
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"圖檔新增有誤: {e}"
            )

    @staticmethod
    async def update_view( db: AsyncSession, data: ShapeNameUpdateBinding) -> ShapesName:
        stmt = (
            update(ShapesName)
            .where(ShapesName.shape_name_id == data.shape_name_id)
            .values(view_id=data.view_id)
            .returning(ShapesName)
        )
        try:
            result = await db.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"shape_name_id={data.shape_name_id} 不存在，無法更新 view_id。"
                )
            await db.commit()
            return row
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error binding parameter view: {e}"
            )

    @staticmethod
    async def update(db: AsyncSession, data: ShapeNameUpdate) -> ShapesName:
        stmt = (
            update(ShapesName)
            .where(ShapesName.shape_name_id == data.shape_name_id)
            .values(**data.model_dump(exclude={"svgObjects", "old_name", "shape_name_id"}))
            .returning(ShapesName)
        )
        try:
            result = await db.execute(stmt)
            row = result.scalar_one_or_none()   # 找不到就回傳 None，不拋
            if row is None:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                                    , detail=f"shape_name_id={data.shape_name_id} 不存在，無法更新。")           
            if row:
                await db.commit()            
            return row   
        
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__SHAPES_NA__view" in msg:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST 
                                    , detail="無效的 view_id，該視圖不存在。")    
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing image file: {e}"
            )


    @staticmethod
    async def update_pic(data: ShapeNameUpdate):        
        try:

            old_path = cfg.image_dir/data.old_name
            new_path =cfg.image_dir / data.name

            # old_path = IMG_DIR / data.old_name
            # new_path =IMG_DIR / data.name

            old_ext = data.old_name.lower().split(".")[-1]
            new_ext = data.name.lower().split(".")[-1]

            if old_ext == "svg" and new_ext == "svg":
                if data.old_name != data.name:
                    os.rename(old_path, new_path)
                    
                with open(new_path, "w", encoding="utf-8") as f:
                    f.write(data.svgObjects)

            elif old_ext == "png" and new_ext == "png":
                if data.old_name != data.name:
                    os.rename(old_path, new_path)
                    
                _, b64 = data.svgObjects.split(",",1)
                data = base64.b64decode(b64)
                with open(new_path, "wb") as f:
                    f.write(data)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST
                                    , detail=f"請使用相同副檔名: {data.old_name}無法改為{data.name}") 
        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                                , detail=f"原圖檔不存在: {data.old_name}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"圖檔更改有誤：{e}")


    @staticmethod
    async def delete(db: AsyncSession, sid: int) -> None:
         # 1) 先檢查 ELEMENTS_SHAPES、VIEW_SHAPES 裡的參照
        sel1 = select(ElementsShapes.elem_shapes_id.label("id"))\
               .where(ElementsShapes.shape_name_id == sid)
        sel2 = select(ViewShape.view_shape_id.label("id"))\
               .where(ViewShape.shape_name_id == sid)

        union = union_all(sel1, sel2)
        result = await db.execute(union)
        refs = result.scalars().all()

        if refs:
            # 有參照就拒絕
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                  f"刪除失敗：shape_name_id={sid} "
                  f"尚被參照於 ELEMENTS_SHAPES/VIEW_SHAPES (ids: {refs})"
                )
            )       
        
        

        await db.execute(delete(ShapesName).where(ShapesName.shape_name_id == sid))
        await db.commit()


    @staticmethod
    async def delete_pic(name: str) :
        file_path = cfg.image_dir / name
        try:        
            os.remove(file_path)
        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_202_ACCEPTED,
                                detail=f"圖檔不存在: {name}")            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("刪除圖檔有誤:{e}")

    # response 要 shape_name 非 name 
    # @staticmethod
    # async def get_all(db: AsyncSession) -> list[ShapesName]:
    #     return (await db.execute(select(ShapesName))).scalars().all()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[ShapeNameResp]:
        j = (
            join(ShapesName, Views,  ShapesName.view_id  == Views.view_id,  isouter=True)
        )

        stmt = (
            select(
                ShapesName.shape_name_id,
                ShapesName.name.label("shape_name"),
                ShapesName.group_width,
                ShapesName.group_height,
                ShapesName.group_y,
                ShapesName.view_id,
                ShapesName.link_URL,
                ShapesName.svg_tag,
                Views.name.label("view_name"),
            )            
            .select_from(j)
        )

        result = await db.execute(stmt)
        rows = result.mappings().all()
        return [ShapeNameResp(**r) for r in rows]

        # result = await db.execute(select(ShapesName))
        # objs = result.scalars().all()        
        # # 將每個 object 的 name 改為 shape_name，並轉 Pydantic
        # return [
        #     ShapeNameResp.model_validate(
        #         {**r.__dict__, "shape_name": r.name},  # 加入 shape_name
        #         from_attributes=True
        #     ) for r in objs
        # ]

    @staticmethod
    async def get_by_id(db: AsyncSession, shape_name_id: int) -> ShapesName | None:
        try:
            stmt = (
                select(
                    ShapesName.shape_name_id,
                    ShapesName.name,#.label("shape_name"),
                    ShapesName.group_width,
                    ShapesName.group_height,
                    ShapesName.group_y,
                    ShapesName.view_id,
                    ShapesName.link_URL,
                    ShapesName.svg_tag,
                )
                .where(ShapesName.shape_name_id == shape_name_id)
            )

            result = await db.execute(stmt)
            row = result.mappings().first()
            if row:
                return row
            # return None
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"圖檔不存在 {shape_name_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"取得圖檔{shape_name_id}有誤:{e}")

    @staticmethod
    async def full_detail(db: AsyncSession, sid: int) -> list[dict]:
        """回傳 shape and shape_name ，但我想把 shape 移除"""
        # 把 Shapes.__table__.columns 攤平，並排除我們不想重複的 FK
        shape_cols = [
            c for c in Shapes.__table__.columns
            #if c.name != "shape_name_id"
        ]

        j = (
            join(ShapesName, Shapes, ShapesName.shape_name_id == Shapes.shape_name_id)
            .join(Views, ShapesName.view_id == Views.view_id, isouter=True)
        )
        stmt = (
            select(
                ShapesName.name.label("shape_name"),
                ShapesName.link_URL,
                ShapesName.view_id,
                Views.name.label("view_name"),
                ShapesName.svg_tag,
                *shape_cols,
                # Shapes.shape_name_id,
                # Shapes.shape_id,
                # Shapes.shape_type,
                # Shapes.x,
                # Shapes.y,
                # Shapes.zoom,
                # Shapes.is_popup,
                # Shapes.is_shine,
                # Shapes.tooltips,
                # Shapes.width,
                # Shapes.height,
                # Shapes.fill_color,
                # Shapes.fill_style,
                # Shapes.border_color,
                # Shapes.border_width,
                # Shapes.angle,
                # Shapes.group_order,
                ShapesName.group_y,
                ShapesName.group_width,
                ShapesName.group_height,
            )
            .select_from(j)
            .where(ShapesName.shape_name_id == sid)
            .order_by(Shapes.shape_name_id)
        )
        rows = (await db.execute(stmt)).mappings().all()   # 回傳 list[RowMapping]
        return [dict(r) for r in rows]