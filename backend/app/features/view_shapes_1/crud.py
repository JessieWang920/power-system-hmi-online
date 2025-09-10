"""
TODO: 後續修正 shape 這個tb 可以直接步要，可以移除一些 根本沒用的欄位減少 query 時間

[view_shape] 抓出 elem_id 有值的部分，並帶入狀態
TODO: 要再測試DI AI
"""
from typing import List, AsyncIterator, Dict, Any
import orjson
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter

from .schema import ViewShapeResp, FunctionItem    # ← 直接引用你提供的 schema


_ULTRA_SQL = text(r"""
SELECT
    vw.view_id,
    vw.name                        AS view_name,
    vw.height                      AS view_height,
    vw.width                       AS view_width,
    vw.backgroundColor             AS view_backgroundColor,
    vw.svg_tag,
    vw.view_type,

    vs.view_shape_id,
    vs.view_shape_order,
    vs.x                           AS view_x,
    vs.y                           AS view_y,

    el.elem_id,
    el.name                        AS elem_name,
    el.point_id,
    el.link_URL                    AS elem_link_URL,
    el.view_id                     AS elem_view_id,
    el.isLock,
    vw2.view_type                  AS elem_view_type,

    pn.point_id,
    pn.name                        AS point_name,
    pn.di_id,
    pn.ai_id,
    pn.do_id,
    pn.sdi_id,

    pt.partition_id,
    pt.name                        AS partition_name,

    es.elem_shapes_id,
    es.status,
    es.statu_default,
    es.shape_name_id,

    spn.name                       AS shapes_name,
    spn.svg_tag                    AS shapes_name_svg_tage,
    spn.group_y,
    spn.group_width,
    spn.group_height,
    spn.view_id                    AS shapes_name_view_id,
    spn.link_URL,

    /*sp.shape_type,
    sp.x,
    sp.y,
    sp.zoom,
    sp.is_popup,
    sp.is_shine,
    sp.tooltips,
    sp.width,
    sp.height,
    sp.fill_color,
    sp.fill_style,
    sp.border_color,
    sp.border_width,
    sp.angle,
    sp.group_order,*/

    /* ---------- function 聚合 ---------- */
    ISNULL((
        SELECT
            p2.point_id          AS link_point_id,
            p2.name              AS link_point_name,
            p2.partition_id      AS link_partition_id,
            p2.ai_id             AS link_ai_id,
            pt2.name             AS link_partition_name,
            ff.formula_order,
            ff.setValue,
            ff.isTrue_operand_type,
            ff.isTrue,
            ff.isFalse_operand_type,
            ff.isFalse,
            ff.function_id,
            ff.fu_operator_id,
            fl.name              AS list_name,
            fl.parameters,
            fo.name              AS operator_name
        FROM functions_points   fp
        JOIN points             p2  ON fp.point_id      = p2.point_id
        JOIN partition          pt2 ON p2.partition_id  = pt2.partition_id
        JOIN functions_formula  ff  ON fp.fu_formula_id = ff.fu_formula_id
        JOIN functions_operator fo  ON fo.fu_operator_id= ff.fu_operator_id
        JOIN functions_list     fl  ON fl.function_id   = ff.function_id
        WHERE fp.sdi_id = pn.sdi_id
        ORDER BY ff.formula_order
        FOR JSON PATH
    ), '[]')                     AS function_json,

    /* ---------- do_list 聚合 ---------- */
    ISNULL((
        SELECT
            dl.do_id,
            p3.name              AS do_name,
            pt3.partition_id     AS do_partition_id,
            pt3.name             AS do_partition_name
        FROM do_list      dl
        JOIN points       p3  ON dl.do_id        = p3.do_id
        JOIN partition    pt3 ON p3.partition_id = pt3.partition_id
        WHERE dl.point_id = pn.point_id
        FOR JSON PATH
    ), '[]')                     AS do_list_json

    FROM  VIEWS               vw
    LEFT JOIN VIEW_SHAPES     vs  ON vw.view_id        = vs.view_id AND vs.elem_id IS NOT NULL
    LEFT JOIN ELEMENTS        el  ON vs.elem_id        = el.elem_id
    LEFT JOIN VIEWS           vw2 ON vw2.view_id       = el.view_id
    LEFT JOIN POINTS          pn  ON pn.point_id       = el.point_id
    LEFT JOIN PARTITION       pt  ON pt.partition_id   = pn.partition_id
    LEFT JOIN ELEMENTS_SHAPES es  ON es.elem_id        = el.elem_id
    LEFT JOIN SHAPES_NAME     spn ON spn.shape_name_id = es.shape_name_id
    /*LEFT JOIN SHAPES          sp  ON sp.shape_name_id  = spn.shape_name_id*/
    WHERE vs.view_id = :view_id         
    ORDER BY vs.view_shape_order;
    """)

class ViewShapeCRUD:
    @staticmethod
    async def _row_to_resp(row: Dict[str, Any]) -> ViewShapeResp:
        """
        把單列 row 轉成 ViewShapeResp
        """
        # 1. 先把基礎欄位挑出
        base: Dict[str, Any] = {
            k: row[k]
            for k in row.keys()
            if k not in ("function_json", "do_list_json")
        }


        func_items_raw = orjson.loads(row["function_json"])
        # 讓 Pydantic 自動把 list[dict] 轉 list[FunctionItem]
        func_items = TypeAdapter(List[FunctionItem]).validate_python(func_items_raw)

        # # 2. 將 function_json → List[FunctionItem]
        # func_items = [
        #     FunctionItem(**f) for f in orjson.loads(row["function_json"])
        # ]

        # 3. do_list 還沒定義 schema，先維持 list[dict]
        do_items = orjson.loads(row["do_list_json"])

        # 4. 建構 ViewShapeResp
        return ViewShapeResp(**base, function=func_items, do_list=do_items)

    @classmethod
    async def get_view_shapes(
        cls,
        db: AsyncSession,
        view_id: int
    ) -> List[ViewShapeResp]:
        """
        一次回傳 List[ViewShapeResp]
        """
        result = await db.stream(_ULTRA_SQL, {"view_id": view_id})
        data =  [
            await cls._row_to_resp(row)
            async for row in result.mappings()
        ]
        return data



# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import text, select, bindparam
# from typing import List
# from app.core.logger import get_logger
# from .schema import ViewShapeResp
# from collections import defaultdict

# logger = get_logger(__name__)
# class ViewShapeCRUD:
#     # == 主要資料 ==    
#     # 先找出 [VIEW] 及 [VIEW_SHAPE] 符合:view_id 的資料，且elem_id 要有值
#     # 再 JOIN [ELEMENTS] 出 元素相關資料
#     _MAIN_SQL = text("""
#     -- ★ 這段就是你在 Node-RED 「ELEM_ID READ FUNCTION」 組出來的 SQL
#     SELECT
#             vw.view_id , vw.name               AS view_name ,
#             vw.height  AS view_height , vw.width AS view_width ,
#             vw.backgroundColor AS view_backgroundColor ,
#             vw.svg_tag , vw.view_type,
#             vs.view_shape_id , vs.view_shape_order , vs.x AS view_x , vs.y AS view_y ,
#             el.elem_id , el.name              AS elem_name ,
#             pn.point_id , pn.name             AS point_name ,
#             pn.di_id , pn.ai_id , pn.do_id , pn.sdi_id ,
#             pt.partition_id , pt.name         AS partition_name ,
#             es.elem_shapes_id , es.status , es.statu_default , es.shape_name_id ,
#             spn.name          AS shapes_name ,
#             spn.svg_tag       AS shapes_name_svg_tage ,
#             spn.group_y , spn.group_width , spn.group_height ,
#             sp.shape_id , sp.shape_type , sp.x , sp.y , sp.zoom ,
#             sp.is_popup , sp.is_shine , sp.tooltips , sp.width , sp.height ,
#             sp.fill_color , sp.fill_style , sp.border_color , sp.border_width ,
#             sp.angle , sp.group_order
#         FROM VIEWS           vw
#         LEFT JOIN VIEW_SHAPES vs  ON vw.view_id = vs.view_id  AND vs.elem_id IS NOT NULL
#         JOIN ELEMENTS         el  ON vs.elem_id = el.elem_id
#         JOIN POINTS           pn  ON pn.point_id = el.point_id
#         JOIN PARTITION        pt  ON pt.partition_id = pn.partition_id
#         JOIN ELEMENTS_SHAPES  es  ON es.elem_id   = vs.elem_id
#         JOIN SHAPES_NAME      spn ON spn.shape_name_id = es.shape_name_id
#         JOIN SHAPES           sp  ON sp.shape_name_id  = spn.shape_name_id
#         WHERE vs.view_id = :view_id
#         ORDER BY es.statu_default ASC
#     """)

#     # == sub 查詢 (每筆 shape 再拆) ==
#     _SUB_SQL = text("""
#     SELECT * FROM {table} WHERE shape_id = :shape_id
#     """)

#     # == function 查詢 ==
#     # _FUNC_SQL = text("""
#     # SELECT
#     #   pn.point_id   AS link_point_id,
#     #   pn.name       AS link_point_name,
#     #   pn.partition_id AS link_partition_id,
#     #   pn.ai_id      AS link_ai_id,
#     #   pt.name       AS link_partition_name,
#     #   ff.formula_order, ff.setValue, ff.isTrue_operand_type,
#     #   ff.isTrue, ff.isFalse_operand_type, ff.isFalse,
#     #   ff.function_id, ff.fu_operator_id,
#     #   fl.name       AS list_name,
#     #   fl.parameters,
#     #   fo.name       AS operator_name
#     # FROM sdi_list sdi
#     # LEFT JOIN functions_points   fp ON sdi.sdi_id   = fp.sdi_id
#     # LEFT JOIN points             pn ON fp.point_id  = pn.point_id
#     # LEFT JOIN functions_formula  ff ON fp.fu_formula_id = ff.fu_formula_id
#     # LEFT JOIN functions_operator fo ON fo.fu_operator_id = ff.fu_operator_id
#     # LEFT JOIN functions_list     fl ON fl.function_id    = ff.function_id
#     # LEFT JOIN partition          pt ON pn.partition_id   = pt.partition_id
#     # WHERE sdi.sdi_id = :sdi_id
#     # ORDER BY ff.formula_order
#     # """)
#     _FUNC_SQL_MULTI = text("""
#         SELECT
#         sdi.sdi_id,
#         pn.point_id   AS link_point_id,
#         pn.name       AS link_point_name,
#         pn.partition_id AS link_partition_id,
#         pn.ai_id      AS link_ai_id,
#         pt.name       AS link_partition_name,
#         ff.formula_order, ff.setValue, ff.isTrue_operand_type,
#         ff.isTrue, ff.isFalse_operand_type, ff.isFalse,
#         ff.function_id, ff.fu_operator_id,
#         fl.name       AS list_name,
#         fl.parameters,
#         fo.name       AS operator_name
#         FROM sdi_list sdi
#         LEFT JOIN functions_points   fp ON sdi.sdi_id   = fp.sdi_id
#         LEFT JOIN points             pn ON fp.point_id  = pn.point_id
#         LEFT JOIN functions_formula  ff ON fp.fu_formula_id = ff.fu_formula_id
#         LEFT JOIN functions_operator fo ON fo.fu_operator_id = ff.fu_operator_id
#         LEFT JOIN functions_list     fl ON fl.function_id    = ff.function_id
#         LEFT JOIN partition          pt ON pn.partition_id   = pt.partition_id
#         WHERE sdi.sdi_id IN :sdi_ids
#         ORDER BY sdi.sdi_id, ff.formula_order
#         """).bindparams(bindparam("sdi_ids", expanding=True))

#     # == do_list 查詢 ==
#     # _DO_SQL = text("""
#     # SELECT
#     #   dl.do_id,
#     #   pn2.name          AS do_name,
#     #   pt2.partition_id  AS do_partition_id,
#     #   pt2.name          AS do_partition_name
#     # FROM do_list dl
#     # LEFT JOIN points    pn2 ON dl.do_id = pn2.do_id
#     # LEFT JOIN partition pt2 ON pn2.partition_id = pt2.partition_id
#     # WHERE dl.point_id = :point_id
#     # """)
#     _DO_SQL_MULTI = text("""
#         SELECT
#         pn.point_id,
#         dl.do_id,
#         pn2.name         AS do_name,
#         pt2.partition_id AS do_partition_id,
#         pt2.name         AS do_partition_name
#         FROM do_list dl
#         LEFT JOIN points pn2        ON dl.do_id = pn2.do_id
#         LEFT JOIN partition pt2     ON pn2.partition_id = pt2.partition_id
#         JOIN points pn              ON dl.point_id = pn.point_id
#         WHERE pn.point_id IN :point_ids
#         """).bindparams(bindparam("point_ids", expanding=True))

#     @classmethod
#     async def get_view_shapes(cls, db: AsyncSession, view_id: int) -> list[ViewShapeResp]:
#         rows = (await db.execute(cls._MAIN_SQL, {"view_id": view_id})).mappings().all()

#         # ---------- 1) 先收集所有要用的 key ----------
#         sdi_ids    = {r["sdi_id"]   for r in rows if r["sdi_id"]}
#         point_ids  = {r["point_id"] for r in rows if r["point_id"]}

#         # ---------- 2) 一次撈 function ----------
#         func_map: dict[int, list[dict]] = defaultdict(list)
#         if sdi_ids:
#             funcs = (await db.execute(cls._FUNC_SQL_MULTI, {"sdi_ids": tuple(sdi_ids)})).mappings().all()
#             for f in funcs:
#                 func_map[f["sdi_id"]].append(dict(f))

#         # ---------- 3) 一次撈 do_list ----------
#         do_map: dict[int, list[dict]] = defaultdict(list)
#         if point_ids:
#             dos = (await db.execute(cls._DO_SQL_MULTI, {"point_ids": tuple(point_ids)})).mappings().all()
#             for d in dos:
#                 do_map[d["point_id"]].append(dict(d))

#         # ---------- 4) 組合最終回傳 ----------
#         resp = []
#         for r in rows:
#             data = dict(r)

#             # sub 查詢（若要優化也可一次抓，這裡先保留原本的）
#             # ...

#             data["function"] = func_map.get(r["sdi_id"], [])
#             data["do_list"]  = do_map.get(r["point_id"], [])
#             resp.append(ViewShapeResp(**data))

#         return resp
    
#     # @classmethod
#     # async def get_view_shapes(cls, db: AsyncSession, view_id: int) -> List[ViewShapeResp]:
#     #     rows = (await db.execute(cls._MAIN_SQL, {"view_id": view_id})).mappings().all()
#     #     resp: list[dict] = []

#     #     for r in rows:
#     #         data = dict(r)

#     #         # ---- sub 查詢：根據 shape_type 決定資料表 ----
#     #         table_map = {
#     #             0: "SHAPES_ELLIPSE", 1: "SHAPES_RECTANGLE", 2: "SHAPES_POLYGON",
#     #             3: "SHAPES_CIRCLE",  4: "SHAPES_LINE",      5: "SHAPES_TEXT",
#     #             6: "SHAPES_IMG",     7: "SHAPES_ARC"
#     #         }
#     #         tbl = table_map.get(r["shape_type"])
#     #         if tbl and r["shape_id"]:
#     #             sub_sql = text(f"SELECT * FROM {tbl} WHERE shape_id = :shape_id") 
#     #             sub_rows = (await db.execute(sub_sql, {"shape_id": r["shape_id"]})).mappings().all()
#     #             # sub_rows = (await db.execute(
#     #             #     cls._SUB_SQL.bindparams(table=text(tbl)), {"shape_id": r["shape_id"]}
#     #             # )).mappings().all()
#     #             data["sub"] = sub_rows

#     #         # ---- function 查詢 ----
#     #         if r["sdi_id"]:
#     #             func_rows = (await db.execute(cls._FUNC_SQL, {"sdi_id": r["sdi_id"]})).mappings().all()
#     #             data["function"] = func_rows

#     #         # ---- do_list 查詢 ----
#     #         if r["point_id"]:
#     #             do_rows = (await db.execute(cls._DO_SQL, {"point_id": r["point_id"]})).mappings().all()
#     #             data["do_list"] = do_rows

#     #         resp.append(ViewShapeResp(**data))

#     #     return resp
