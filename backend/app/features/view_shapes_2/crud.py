"""
TODO: 後續修正 shape 這個tb 可以直接步要，可以移除一些 根本沒用的欄位減少 query 時間

[view_shape] 抓出 elem_id 有值的部分，並帶入狀態
TODO: 要再測試DI AI
"""
from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import get_logger
from app.features.views.model import Views
from app.features.view_shapes.model import ViewShape
from app.features.shapes_name.model import ShapesName
from app.features.shapes.model import Shapes

logger = get_logger(__name__)

class ViewShapeCRUD:
    @staticmethod
    async def get_by_view(db: AsyncSession, view_id: int) -> list[dict]:
        # 依你的 Node-RED SQL 改寫
        vw2 = aliased(Views)
        stmt = (
            select(
                Views.view_id,
                Views.name.label("view_name"),
                Views.height.label("view_height"),
                Views.width.label("view_width"),
                Views.backgroundColor.label("view_backgroundColor"),

                ViewShape.view_shape_id,
                ViewShape.view_shape_order,
                ViewShape.x.label("view_x"),
                ViewShape.y.label("view_y"),

                ShapesName.name.label("shapes_name"),
                ShapesName.svg_tag,
                ShapesName.group_y,
                ShapesName.group_width,
                ShapesName.group_height,
                ShapesName.link_URL.label("shapes_name_link_URL"),
                ShapesName.view_id.label("shapes_name_view_id"),
                ShapesName.shape_name_id,
                vw2.view_type.label("shapes_name_view_type"),
                

                # Shapes.shape_id,
                # Shapes.shape_name_id,
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
            )
            .join(ViewShape, ViewShape.view_id == Views.view_id)
            .join(ShapesName, ShapesName.shape_name_id == ViewShape.shape_name_id)
            .join(vw2, vw2.view_id == ShapesName.view_id, isouter=True)
            # .join(Shapes, Shapes.shape_name_id == ViewShape.shape_name_id)
            .where(ViewShape.view_id == view_id)
            .order_by(ViewShape.view_shape_order)
        )
        rows = (await db.execute(stmt)).mappings().all()
        return [dict(r) for r in rows]
