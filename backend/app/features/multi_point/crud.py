import openpyxl
import io
from fastapi import UploadFile, HTTPException, status
from typing import Dict
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.features.partition.schema import PartitionCreate
from app.features.partition.crud import PartitionCRUD

from app.features.ai.crud import AICRUD
from app.features.ai.schema import AICreate

from app.features.points.model import Points
from app.features.di.crud import DiCRUD
from app.features.di.schema import DiCreateIn

class MultiPointCRUD:

    @staticmethod
    async def read_file(file: UploadFile,sheet_name:str,db:AsyncSession) -> Dict:
        # try:
            # 直接讀 Excel
            df = pd.read_excel(file.file, sheet_name=sheet_name, engine="openpyxl")
            # 清除空白換行
            df.columns = df.columns.str.replace(r"\s+", "", regex=True) 
            
            # 處理盤名
            for col in ["PanelName", "TagName(PanelName+PointDescription)",
                        "PointDescription", "AIMaxValue", "AIMinValue", "Type",
                        "DI/DOType","PointDescription"]:
                if col not in df.columns:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, f"找不到欄位：{col}")
            
            
            # 取得 Excel 中的唯一 PanelName 名稱
            new_panels = df["PanelName"].dropna().drop_duplicates().astype(str).tolist()           
            # 取得資料庫中已有的 Partition 名稱
            existing_partitions = await PartitionCRUD.get_all(db)
            existing_names = {p.name for p in existing_partitions}

            # 找出尚未存在的名稱
            unique_new_panels = [name for name in new_panels if name not in existing_names]

            # 寫入新的 Partition
            created_ids = []
            for name in unique_new_panels:
                data = PartitionCreate(name=name)
                pid = await PartitionCRUD.create(db, data)
                # created_ids.append({"partition_id": pid, "name": name})

            # 名稱與 partition_id映射
            name_to_pid = {p.name: p.partition_id for p in existing_partitions}
    

            # ── Step 2: 取出目前 POINTS 中 ai_id 不為 null 的點位名稱 ──
            stmt = select(Points.name).where(Points.ai_id.isnot(None))
            rows = await db.execute(stmt)
            existing_point_names = {r[0] for r in rows.fetchall()}

            # ── Step 3: 過濾 Excel 中 Type 為 AI 的資料 ──
            df_ai = df[df["Type"].astype(str).str.upper() == "AI"].copy()
            df_ai = df_ai[["PanelName", "TagName(PanelName+PointDescription)", "AIMaxValue", "AIMinValue"]]

            # ── Step 4: 篩選未重複的 TagName ──
            df_ai["TagName"] = df_ai["TagName(PanelName+PointDescription)"]
            df_ai = df_ai[~df_ai["TagName"].isin(existing_point_names)]

            # ── Step 5: 建立 AI_LIST + POINTS ──
            for _, row in df_ai.iterrows():
                tagname = row["TagName"]
                panelname = row["PanelName"].strip()
                partition_id = name_to_pid.get(panelname)
                ai_min = float(str(row["AIMinValue"]).replace(",", "").strip())
                ai_max = float(str(row["AIMaxValue"]).replace(",", "").strip())
                if not partition_id:
                    # 若找不到 partition 對應，略過（可記 log）
                    continue

                # 準備資料送入 AICRUD.create
                data = AICreate(
                    point_name=tagname,
                    partition_id=partition_id,
                    point_min=ai_min,
                    point_max=ai_max,
                    dataType_id=1  # 預設為 1
                )
                result = await AICRUD.create(db, data)

            # ── Step 6: 取得目前 POINTS 中 di_id 不為 null 的點位名稱 ──
            stmt = select(Points.name).where(Points.di_id.isnot(None))
            rows = await db.execute(stmt)
            existing_di_names = {r[0] for r in rows.fetchall()}

            # ── Step 7: 過濾 Excel 中 Type 為 DI 的資料 ──
            df_di = df[df["Type"].astype(str).str.upper() == "DI"].copy()
            df_di = df_di[["PanelName", "TagName(PanelName+PointDescription)",
                            "PointDescription", "DI/DOType"]]
            df_di["TagName"] = df_di["TagName(PanelName+PointDescription)"]
            # 篩選尚未存在的 TagName
            df_di = df_di[~df_di["TagName"].isin(existing_di_names)]
            df_di["DI/DOType"] = (
                df_di["DI/DOType"].astype(str).str.strip().replace({"DPS": 2, "SPS": 1})
            )

            # ── Step 8: 建立 DI_LIST + POINTS ──
            for _, row in df_di.iterrows():
                tagname = row["TagName"]
                panelname = row["PanelName"]
                point_des = row["PointDescription"]
                point_num  = row["DI/DOType"]
                partition_id = name_to_pid.get(panelname)
                if not partition_id:
                    # 找不到對應 partition，就略過
                    continue

                data = DiCreateIn(
                    point_name=tagname,
                    partition_id=partition_id,
                    point_des=point_des,
                    point_num=point_num
                )
                result = await DiCRUD.create(db, data)

            return {                
                "filename": file.filename,
                "sheet_name": sheet_name,
                "ai_count": len(df_ai),
                "di_count": len(df_di),
            }

