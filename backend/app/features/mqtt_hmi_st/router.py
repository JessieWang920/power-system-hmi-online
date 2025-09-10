from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from .crud import MqttStCrud
from .schema import MqttStResp
from app.core.security_basic import basic_auth

router = APIRouter(prefix="/MQTT_HMI_ST", tags=["MQTT HMI ST"],dependencies=[Depends(basic_auth)])

@router.get("", response_model=list[MqttStResp])
async def list_mx(
    limit: int = Query(1000, ge=1, le=10000, description="最多一次抓多少筆（依 time DESC）"),
    db: AsyncSession = Depends(get_db),
):
    rows = await MqttStCrud.read_all(db, limit)
    # 轉成前端期望格式
    return [
        {
            "Type": "ST",
            "Content": {
                "TagName": r.tag_name,
                "Value":   r.value,
                "Time":    r.time,
                "Quality": r.quality,
            },
        }
        for r in rows
    ]
