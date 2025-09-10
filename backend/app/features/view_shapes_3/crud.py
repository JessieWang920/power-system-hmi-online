# backend/app/features/view_shapes/crud.py
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.logger import get_logger

from app.features.views.model import Views
from app.features.view_shapes.model import ViewShape
from app.features.ai_objects_text.model import AIObjectsText
from app.features.points.model import Points
from app.features.partition.model import Partition
from app.features.ai.model import AIList
from app.features.ai_datatype_list.model import AiDataTypeList


logger = get_logger(__name__)

class ViewShapesCRUD:
    @staticmethod
    async def list_by_view_id(db: AsyncSession, view_id: int):
        if view_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="view_id 必填")

        j = (
            join(Views,        ViewShape,      Views.view_id == ViewShape.view_id)
            .join(AIObjectsText, ViewShape.ai_objectText_id == AIObjectsText.ai_objectText_id)
            .join(Points,        AIObjectsText.point_id == Points.point_id, isouter=True)
            .join(Partition,     Points.partition_id == Partition.partition_id, isouter=True)
            .join(AIList,        Points.ai_id == AIList.ai_id, isouter=True)
            .join(AiDataTypeList,    AIList.dataType_id == AiDataTypeList.data_type_id, isouter=True)
        )

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
                AIObjectsText.ai_objectText_id,
                AIObjectsText.name.label("ai_objectText_name"),
                AIObjectsText.font_family,
                AIObjectsText.font_style,
                AIObjectsText.font_size,
                AIObjectsText.text,
                AIObjectsText.font_color,
                AIObjectsText.unit,
                Points.point_id,
                Points.name.label("point_name"),
                Points.di_id,
                Points.ai_id,
                Points.do_id,
                Points.sdi_id,
                Partition.partition_id,
                Partition.name.label("partition_name"),
                AiDataTypeList.name.label("dataType_name"),
            )
            .select_from(j)
            .where(Views.view_id == view_id)
            .order_by(ViewShape.view_shape_order)
        )

        rows = (await db.execute(stmt)).mappings().all()
        # if not rows:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        #                         detail=f"view_id={view_id} 找不到資料")

        return rows
