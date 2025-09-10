from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from fastapi import HTTPException, status

from .model import AIList
from app.features.points.model import Points
from app.features.ai_datatype_list.model import AiDataTypeList 
from app.features.partition.model import Partition
from app.features.ai_objects_text.model import AIObjectsText
from .schema import (
    AICreate, AIUpdate,
    PointCreateResp, AIUpdateResp, AIDetail, AIDelete
)

class AICRUD:

    @staticmethod
    async def create(db: AsyncSession, data: AICreate) -> PointCreateResp:
        """
        1) 新增 AIList
        2) 新增 Points（綁 ai_id）
        """
        try:
            ai = AIList(
                dataType_id=data.dataType_id,
                ai_min=data.point_min,
                ai_max=data.point_max
            )
            db.add(ai)
            await db.flush()

            pt = Points(
                name=data.point_name,
                partition_id=data.partition_id,
                ai_id=ai.ai_id
            )
            db.add(pt)
            await db.commit()

            # logger.info(
            #     f"AI.create 成功: ai_id={ai.ai_id}, point_id={pt.point_id}, "
            #     f"partition_id={pt.partition_id}, name={pt.name}"
            # )


            return PointCreateResp(
                point_id=pt.point_id,
                name=pt.name,
                partition_id=pt.partition_id,
                ai_id=pt.ai_id
            )
       
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(f"AI.create 資料庫錯誤，data={data}")
            raise
        except Exception:
            await db.rollback()
            logger.exception(f"AI.create 未預期錯誤，data={data}")
            raise
       
    @staticmethod
    async def update(db: AsyncSession, data: AIUpdate) -> AIUpdateResp:
        # UPDATE AI_LIST
        res = await db.execute(
            update(AIList)
            .where(AIList.ai_id == data.ai_id)
            .values(dataType_id=data.dataType_id,
                    ai_min=data.point_min,
                    ai_max=data.point_max)
            .returning(AIList.dataType_id, AIList.ai_min, AIList.ai_max)
        )
        row = res.first()

        # UPDATE POINTS
        await db.execute(
            update(Points)
            .where(Points.point_id == data.point_id)
            .values(name=data.point_name)
        )
        await db.commit()

        return AIUpdateResp(
            dataType_id=row.dataType_id,
            ai_min=row.ai_min,
            ai_max=row.ai_max
        )

    @staticmethod
    async def delete(db: AsyncSession, data: AIDelete) -> None:
        """先刪 Points 再刪 AIList"""
        try:
            await db.execute(delete(Points).where(Points.point_id == data.point_id))
            await db.execute(delete(AIList).where(AIList.ai_id == data.ai_id))
            await db.commit()
        except IntegrityError as e:
                await db.rollback()
                raw = getattr(e, "orig", None)
                msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
                if "FK__AI_Object__point_" in msg:
                    detail = f"該點位已綁定物件"
                else:
                    detail = f"更新失敗：{msg}"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e


    @staticmethod
    async def list_by_partition(db: AsyncSession, pid: int) -> list[AIDetail]:
        """依 partition_id 取得 AI 詳細清單，並 group elements"""
        try:
            # 1) SELECT 所有需要的欄位
            stmt = (
                select(
                    Points.point_id,
                    Points.name.label("point_name"),
                    Points.partition_id,
                    Partition.name.label("partition_name"),
                    AIList.ai_id,
                    AIList.dataType_id,
                    AIList.ai_max.label("point_max"),
                    AIList.ai_min.label("point_min"),
                    AiDataTypeList.name.label("dataType_name"),
                    AiDataTypeList.input_max,
                    AiDataTypeList.output_max,
                    AIObjectsText.ai_objectText_id,
                    AIObjectsText.name.label("ai_obj_name"),
                    AIObjectsText.unit,
                )
                .select_from(Points)
                .join(AIList, Points.ai_id == AIList.ai_id)
                .join(Partition, Partition.partition_id == Points.partition_id)
                .join(AiDataTypeList, AiDataTypeList.data_type_id == AIList.dataType_id)
                .outerjoin(AIObjectsText, AIObjectsText.point_id == Points.point_id)
                .where(Points.partition_id == pid)
            )

            rows = (await db.execute(stmt)).all()

            # 2) 把 Mapping 轉成純 dict，並 group elements
            grouped: dict[int, dict] = {}
            for row in rows:
                try:
                    m = dict(row._mapping)   # keys 都是純字串了
                    key = m["point_id"]
                    if key not in grouped:
                        # 先把所有欄位攤平
                        grouped[key] = {
                            "point_id":       m["point_id"],
                            "point_name":     m["point_name"],
                            "partition_id":   m["partition_id"],
                            "partition_name": m["partition_name"],
                            "ai_id":          m["ai_id"],
                            "dataType_id":    m["dataType_id"],
                            "point_max":      m["point_max"],
                            "point_min":      m["point_min"],
                            "dataType_name":  m["dataType_name"],
                            "inputMax":       m["input_max"],
                            "ouptMax":        m["output_max"],
                            "elements":       []
                        }
                    grouped[key]["elements"].append({
                        "ai_objectText_id": m["ai_objectText_id"],
                        "ai_obj_name":      m["ai_obj_name"],
                        "unit":             m["unit"],
                    })
                except Exception:
                    # 單列成形失敗不阻斷整體流程
                    logger.exception(f"AI.list_by_partition 組裝單列資料失敗，row={row}")
                    continue

            # 3) 最後把 grouped value 轉成 AIDetail
            return [AIDetail(**v) for v in grouped.values()]

        except SQLAlchemyError:
            logger.exception(f"AI.list_by_partition 查詢資料庫錯誤，partition_id={pid}")
            raise
        except Exception:
            logger.exception(f"AI.list_by_partition 未預期錯誤，partition_id={pid}")
            raise