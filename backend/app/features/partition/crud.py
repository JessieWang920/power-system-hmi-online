from sqlalchemy import select, update, delete,text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from .model import Partition
from .schema import (
    PartitionCreate, PartitionOut, PartitionUpdate,PartitionWithPoints
)
from app.features.points.model import Points

class PartitionCRUD:

    # ── C ──────────────────────────────
    @staticmethod
    async def create(db: AsyncSession, data: PartitionCreate) -> int:
        """
        建立一筆資料，生成PK partition_id
        """
        obj = Partition(name=data.name)    # 把傳入資料包成 ORM 物件
        db.add(obj)                        # 加入資料庫的 staged 區
        await db.flush()                   # 發送 INSERT 指令給 DB，但還沒真正 commit
        await db.commit()                  # 真正提交到資料庫
        return obj.partition_id            # 回傳自動生成的主鍵


    # ── R ──────────────────────────────
    @staticmethod
    async def get_all(db: AsyncSession) -> list[PartitionOut]:
        """取得整張表的所有資料"""
        result = await db.execute(select(Partition))  # 發出 SELECT * FROM PARTITION
        return [PartitionOut.model_validate(i) for i in result.scalars()]

    # @staticmethod
    # async def get(db: AsyncSession, pid: int) -> PartitionOut | None:
    #     """取得特定 partition_id 的資料，若無則為none"""
    #     result = await db.get(Partition, pid)
    #     return PartitionOut.model_validate(result) if result else None

    

    @staticmethod
    async def get_id(
        db: AsyncSession,
        pid: int  
    ) -> list[PartitionWithPoints] :
        """
        取得特定 partition_id 的資料，若無則為none
        並且與 POINTS 做 left join                
        """        
        stmt = (
            select(
                Partition.name.label("partition_name"),
                Points.partition_id,
                Points.name.label("point_name"),
                Points.point_id,
            )
            .select_from(Partition)
            .outerjoin(Points, Partition.partition_id == Points.partition_id)
            .where(Partition.partition_id == pid)
        )
        result = await db.execute(stmt)
        rows = result.all()
        if not rows:
            return []

        return [PartitionWithPoints.model_validate(dict(r._mapping)) for r in rows]

    # ── U ──────────────────────────────
    @staticmethod
    async def update(db: AsyncSession, data: PartitionUpdate) -> None:
        """
        指定partition_id 更新 name

        SQL
        UPDATE partition SET name = '{data.name}' 
        WHERE partition_id = {data.partition_id};
        """
        result = await db.execute(
            update(Partition)
            .where(Partition.partition_id == data.partition_id)
            .values(name=data.name)
            .returning(Partition)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"partition_id={data.partition_id} 不存在，無法刪除"
            )
        await db.commit()

    # ── D ──────────────────────────────
    @staticmethod
    async def delete(db: AsyncSession, pid: int) -> None:
        """
        刪除該partition_id資料

        SQL
        DELETE FROM partition
        WHERE partition_id = {pid}
        """
        row = (await db.execute(select(Partition).where(Partition.partition_id == pid))).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="partition_id 不存在")
        
        await db.execute(delete(Partition).where(Partition.partition_id == pid))
        await db.commit()

