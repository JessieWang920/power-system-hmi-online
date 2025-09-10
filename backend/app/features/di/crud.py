# backend/app/features/di/crud.py
from typing import List, Dict, Any
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, literal_column
from app.core.logger import get_logger
from app.features.points.model import Points
from app.features.partition.model import Partition
from app.features.ai_objects_text.model import AIObjectsText
from app.features.elements.model import Elements   # 你已上傳
from .model import DIList
from .schema import DIDetail

logger = get_logger(__name__)

class DiCRUD:
    @staticmethod
    async def create(db: AsyncSession, data) -> Dict[str, Any]:
        try:
            # 1) 新增 DI_LIST
            res_di = await db.execute(
                insert(DIList).values(point_num=data.point_num, description=data.point_des).returning(DIList.di_id)
            )
            di_id = res_di.scalar_one()
            # 2) 新增 POINTS
            res_pt = await db.execute(
                insert(Points).values(name=data.point_name, partition_id=data.partition_id, di_id=di_id)
                .returning(Points.point_id, Points.name, Points.partition_id, Points.di_id, Points.ai_id, Points.do_id, Points.sdi_id)
            )
            row = res_pt.one()
            await db.commit()
            return dict(row._mapping)
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__POINTS__partitio__24E777C3" in msg:
                detail = "無效的 partition_id，該盤名不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
    
    
    @staticmethod
    async def list_by_partition(db: AsyncSession, pid: int) ->list[DIDetail]:
        # 左連接：POINTS x DI_LIST x PARTITION x ELEMENTS
        stmt = (
            select(
                Points.point_id,
                Points.name.label("point_name"),
                Points.partition_id,
                Partition.name.label("partition_name"),
                Points.di_id,
                DIList.point_num,
                DIList.description.label("point_des"), 
                AIObjectsText.ai_objectText_id,
                AIObjectsText.name.label("ai_obj_name"),
                AIObjectsText.unit,
                Elements.elem_id,
                Elements.name.label("elem_name"),
            )
            .select_from(Points)
            .join(DIList, Points.di_id == DIList.di_id)
            .join(Partition, Partition.partition_id == Points.partition_id)
            .join(Elements, Elements.point_id == Points.point_id, isouter=True)
            .outerjoin(AIObjectsText, AIObjectsText.point_id == Points.point_id)
            .where(Points.partition_id == pid)
        )
        rows = (await db.execute(stmt)).all()

       # 2) 把 Mapping 轉成純 dict，並 group elements
        grouped: dict[int, dict] = {}
        for row in rows:
            m = dict(row._mapping)   # keys 都是純字串了
            key = m["point_id"]
            if key not in grouped:
                # 先把所有欄位攤平
                grouped[key] = {
                    "point_id":       m["point_id"],
                    "point_name":     m["point_name"],
                    "partition_id":   m["partition_id"],
                    "partition_name": m["partition_name"],
                    "di_id":          m["di_id"],
                    "point_num":      m["point_num"],  
                    "point_des":      m["point_des"],
                    "elements":       []
                }
            grouped[key]["elements"].append({
                "ai_objectText_id": m["ai_objectText_id"],
                "ai_obj_name":      m["ai_obj_name"],
                "unit":             m["unit"],
                "elem_id":          m["elem_id"], 
                "elem_name":        m["elem_name"]
            })

        # 3) 最後把 grouped value 轉成 DIDetail
        return [DIDetail(**v) for v in grouped.values()]


    # @staticmethod
    # async def list_by_partition(db: AsyncSession, partition_id: int) -> List[Dict[str, Any]]:
    #     # 左連接：POINTS x DI_LIST x PARTITION x ELEMENTS
    #     base_q = (
    #         select(
    #             Points.point_id,
    #             Points.name.label("point_name"),
    #             Points.partition_id,
    #             Partition.name.label("partition_name"),
    #             Points.di_id,
    #             DIList.point_num,
    #             DIList.description.label("point_des"),
    #             Elements.elem_id,
    #             Elements.name.label("elem_name"),
    #         )
    #         .join(Partition, Points.partition_id == Partition.partition_id)
    #         .join(DIList, Points.di_id == DIList.di_id)
    #         .join(Elements, Elements.point_id == Points.point_id, isouter=True)
    #         .where(Points.partition_id == partition_id)
    #         .order_by(Points.point_id)
    #     )
    #     rows = (await db.execute(base_q)).mappings().all()

    #     # 依 point_id group
    #     # TODO:
    #     merged: Dict[int, Dict[str, Any]] = {}
    #     for r in rows:
    #         pid = r["point_id"]
    #         if pid not in merged:
    #             merged[pid] = {
    #                 "point_id": r["point_id"],
    #                 "point_name": r["point_name"],
    #                 "partition_id": r["partition_id"],
    #                 "partition_name": r["partition_name"],
    #                 "di_id": r["di_id"],
    #                 "point_num": r["point_num"],
    #                 "point_des": r["point_des"],
    #                 "elements": [],
    #             }
    #         # 有 element 才加入；LEFT JOIN 沒對到時 elem_id 會是 None
    #         if r["elem_id"] is not None:
    #             merged[pid]["elements"].append({"elem_id": r["elem_id"], "elem_name": r["elem_name"]})

    #     return list(merged.values())

    @staticmethod
    async def update_one(db: AsyncSession, data) -> Dict[str, Any]:
        # 更新 DI_LIST
        await db.execute(
            update(DIList)
            .where(DIList.di_id == data.di_id)
            .values(point_num=data.point_num, description=data.point_des)
        )
        # 更新 POINTS（name）
        res_pt = await db.execute(
            update(Points)
            .where(Points.point_id == data.point_id, Points.partition_id == data.partition_id)
            .values(name=data.point_name)
            .returning(Points.point_id, Points.name, Points.partition_id, Points.di_id, Points.ai_id, Points.do_id, Points.sdi_id)
        )
        row = res_pt.one_or_none()
        if row is None:
            await db.rollback()
            raise ValueError("point_id / partition_id 不存在或不匹配")
        await db.commit()
        return dict(row._mapping)

    @staticmethod
    async def delete_one(db: AsyncSession, di_id: int, point_id: int, partition_id: int) -> None:
        try:
            # 刪除 POINTS（需 partition_id 防呆）
            await db.execute(
                delete(Points).where(Points.point_id == point_id, Points.partition_id == partition_id)
            )
            # 刪除 DI_LIST
            await db.execute(delete(DIList).where(DIList.di_id == di_id))
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__ELEMENTS__point___797309D9" in msg:
                detail = "該點位已綁定元素，無法刪除。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e