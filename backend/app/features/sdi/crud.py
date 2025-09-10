from sqlalchemy import select, insert, update, delete, text
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.core.logger import get_logger
from app.features.points.model import Points
from .model import SDIList
from .schema import SDIResp,SDIUpdate,SDIDelete

logger = get_logger(__name__)

class SDICRUD:

    # ── 建立 ───────────────────────────────────────
    @staticmethod
    async def create(db: AsyncSession, data:SDIList) -> SDIResp:
        try:
            # 1) SDI_LIST 加一筆資料
            sdi = SDIList(
                name=data.name,
            )
            db.add(sdi)
            await db.flush()

            # 2) POINTS 加一筆資料
            pt = Points(
                name=data.name,
                partition_id=data.partition_id,
                sdi_id=sdi.sdi_id
            )
            db.add(pt)
            await db.commit()

            return SDIResp(
                point_id=pt.point_id,
                name=pt.name,
                partition_id=pt.partition_id,
                sdi_id=pt.sdi_id
            )
        except IntegrityError as e:
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__POINTS__partitio__24E777C3" in msg:
                detail = "無效的 partition_id，該盤名不存在。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e

    # ── 讀取 ───────────────────────────────────────
    @staticmethod
    async def list_by_sdi(db: AsyncSession, sdi_id: int) -> List[Dict[str, Any]]:
        """
        依 sdi_id 取回 SDI 詳細，對應 Node-RED qrytype = 2。
        一筆 SDI 可能對應多條 formula ⇒ 直接 return List。
        """
        sql = text(
            """
            SELECT
                sdi.sdi_id,
                pn.point_id,
                pn.name  AS point_name,
                pt.partition_id,
                pt.name  AS partition_name,
                fp.fu_point_id,
                fp.fu_formula_id,
                ff.formula_order,
                ff.setValue,
                ff.isTrue_operand_type,
                ff.isTrue,
                ff.isFalse_operand_type,
                ff.isFalse,
                ff.function_id,
                ff.fu_operator_id,
                fl.name  AS function_name,
                fl.parameters,
                fo.name  AS operator_name
            FROM SDI_LIST            sdi
            LEFT JOIN functions_points   fp ON sdi.sdi_id   = fp.sdi_id
            LEFT JOIN points             pn ON fp.point_id  = pn.point_id
            LEFT JOIN functions_formula  ff ON fp.fu_formula_id = ff.fu_formula_id
            LEFT JOIN functions_operator fo ON fo.fu_operator_id = ff.fu_operator_id
            LEFT JOIN functions_list     fl ON fl.function_id    = ff.function_id
            LEFT JOIN partition          pt ON pn.partition_id   = pt.partition_id
            WHERE sdi.sdi_id = :sid
            ORDER BY ff.formula_order
            """
        )

        rows = (await db.execute(sql, {"sid": sdi_id})).mappings().all()
        if not rows:
            raise HTTPException(status_code=404, detail=f"sdi_id={sdi_id} 不存在")

        # ── 將同一 (sdi_id, point_id) 合併 sub 陣列 ───────────
        merged: Dict[tuple[int, int], Dict[str, Any]] = {}
        for r in rows:
            key = (r["sdi_id"], r["point_id"])
            if key not in merged:
                merged[key] = {
                    "sdi_id":         r["sdi_id"],
                    "point_id":       r["point_id"],
                    "point_name":     r["point_name"],
                    "partition_id":   r["partition_id"],
                    "partition_name": r["partition_name"],
                    "sub":            [],
                }
            merged[key]["sub"].append(
                {k: r[k] for k in (
                    "fu_point_id", "sdi_id", "point_id", "fu_formula_id",
                    "point_name", "partition_id", "partition_name",
                    "formula_order", "setValue",
                    "isTrue_operand_type", "isTrue",
                    "isFalse_operand_type", "isFalse",
                    "function_id", "fu_operator_id",
                    "function_name", "parameters", "operator_name"
                )}
            )

        return list(merged.values())

    @staticmethod
    async def list_by_partition(db: AsyncSession, partition_id: int) -> List[Dict[str, Any]]:
        """
        先查出 (partition → points → sdi_id)，再對每個 point 查 elements，
        對應 Node-RED qrytype = 1 + READ ELEMENTS 邏輯。
        """
        head_sql = text(
            """
            SELECT
                pt.name AS partition_name,
                pn.partition_id,
                pn.point_id,
                pn.name AS point_name,
                sdi.sdi_id
            FROM SDI_LIST sdi
            LEFT JOIN POINTS    pn ON sdi.sdi_id   = pn.sdi_id
            LEFT JOIN PARTITION pt ON pt.partition_id = pn.partition_id
            WHERE pt.partition_id = :pid
            """
        )

        rows = (await db.execute(head_sql, {"pid": partition_id})).mappings().all()

        # ── 逐點查 elements。單一 partition 量不大，用迴圈最直覺 ──
        elem_sql = text(
            """
            SELECT el.elem_id, el.name AS elem_name
            FROM ELEMENTS      el
            LEFT JOIN POINTS   p   ON p.point_id     = el.point_id
            LEFT JOIN PARTITION pa  ON pa.partition_id = p.partition_id
            LEFT JOIN SDI_LIST sdi ON sdi.sdi_id      = p.sdi_id
            WHERE pa.partition_id = :pid
              AND p.point_id      = :point_id
              AND sdi.sdi_id IS NOT NULL
            """
        )

        result: List[Dict[str, Any]] = []
        for r in rows:
            elem_rows = (
                await db.execute(elem_sql, {"pid": partition_id, "point_id": r["point_id"]})
            ).mappings().all()
            r_dict = dict(r)
            r_dict["elements"] = [dict(e) for e in elem_rows]
            result.append(r_dict)

        return result

    # ── 更新 ───────────────────────────────────────
    @staticmethod
    async def update(db: AsyncSession, data:SDIUpdate) -> SDIResp:
        try:
            async with db.begin():   # 交易區塊，離開時自動 commit
                # 先找 SDI
                sdi: SDIList | None = await db.get(SDIList, data.sdi_id)
                if sdi is None:
                    raise HTTPException(status_code=404, detail=f"sdi_id={data.sdi_id}不存在")
                            
                sdi.name = data.name # 改屬性

                # 找到對應的 Points（以 sdi_id 關聯）
                result = await db.execute(select(Points).where(Points.sdi_id == data.sdi_id))
                pt: Points | None = result.scalar_one_or_none()
                if pt is None:
                    raise HTTPException(status_code=404, detail=f"point_id={data.sdi_id}不存在")

                pt.name = data.name      

            await db.refresh(pt)
            return SDIResp(
                point_id=pt.point_id,
                name=pt.name,
                partition_id=pt.partition_id,
                sdi_id=pt.sdi_id
            )
        except IntegrityError as e:                   # 例如 name 唯一鍵衝突
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="名稱重複或其他完整性錯誤"
            ) from e


    # ── 刪除 ───────────────────────────────────────
    @staticmethod
    async def delete(db: AsyncSession, data:SDIDelete) -> None:
        try:
            await db.execute(delete(Points).where(Points.point_id == data.point_id))
            await db.execute(select(SDIList).where(SDIList.sdi_id == data.sdi_id))        
            await db.commit()
        except IntegrityError as e:                   # 例如 name 唯一鍵衝突
            await db.rollback()
            raw = getattr(e, "orig", None)
            msg = raw.args[1] if raw and len(raw.args) > 1 else str(e)
            if "FK__ELEMENTS__point___797309D9" in msg:
                detail =  "該點位已綁定元素，無法刪除。"
            else:
                detail = f"更新失敗：{msg}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from e
