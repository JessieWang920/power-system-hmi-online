from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .model import AiDataTypeList
from .schema import AiDataTypeCreate, AiDataTypeUpdate, AiDataTypeOut

class AiDataTypeCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: AiDataTypeCreate) -> AiDataTypeOut:
        obj = AiDataTypeList(
            name=data.name,
            input_max=data.input_max,
            input_min=data.input_min,
            output_max=data.output_max,
            output_min=data.output_min,
        )
        db.add(obj)
        await db.flush()
        await db.commit()
        return AiDataTypeOut.model_validate(obj)

    @staticmethod
    async def get_all(db: AsyncSession) -> list[AiDataTypeOut]:
        result = await db.execute(select(AiDataTypeList))
        return [AiDataTypeOut.model_validate(i) for i in result.scalars()]

    @staticmethod
    async def get(db: AsyncSession, dt_id: int) -> AiDataTypeOut | None:
        obj = await db.get(AiDataTypeList, dt_id)
        return AiDataTypeOut.model_validate(obj) if obj else None

    @staticmethod
    async def update(db: AsyncSession, data: AiDataTypeUpdate) -> bool:
        stmt = (
            update(AiDataTypeList)
            .where(AiDataTypeList.data_type_id == data.data_type_id)
            .values(
                name=data.name,
                input_max=data.input_max,
                input_min=data.input_min,
                output_max=data.output_max,
                output_min=data.output_min,
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def delete(db: AsyncSession, dt_id: int) -> bool:
        result = await db.execute(
            delete(AiDataTypeList).where(AiDataTypeList.data_type_id == dt_id)
        )
        await db.commit()
        return result.rowcount > 0
