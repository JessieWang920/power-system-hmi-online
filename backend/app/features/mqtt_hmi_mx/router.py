from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from .crud import MqttMxCrud
from .schema import MqttMxResp
from app.core.security_basic import basic_auth
router = APIRouter(prefix="/MQTT_HMI_MX", tags=["MQTT HMI MX"],dependencies=[Depends(basic_auth)])

@router.get("", response_model=list[MqttMxResp])
async def list_mx(
    limit: int = Query(1000, ge=1, le=10000, description="最多一次抓多少筆（依 time DESC）"),
    db: AsyncSession = Depends(get_db),
):
    rows = await MqttMxCrud.read_all(db, limit)
    # 轉成前端期望格式
    return [
        {
            "Type": "MX",
            "Content": {
                "TagName": r.tag_name,
                "Value":   r.value,
                "Time":    r.time,
                "Quality": r.quality,
            },
        }
        for r in rows
    ]
