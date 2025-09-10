# 新增資料表定義
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class MqttHmiSt(Base):
    __tablename__ = "MQTT_HMI_ST"

    hmi_mx_id = Column(Integer, primary_key=True, autoincrement=True)
    type      = Column(String(2), nullable=False, default="ST")
    tag_name  = Column(String(100), index=True, nullable=False)
    value     = Column(Float, nullable=False)
    time      = Column(DateTime(timezone=True), server_default=func.now())
    quality   = Column(Integer, nullable=False)
