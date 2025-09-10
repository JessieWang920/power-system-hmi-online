"""
定義一個 Partition 類別
對應到資料庫中的一張叫做 PARTITION 的資料表
並描述它的欄位結構
"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Partition(Base):
    __tablename__ = "PARTITION"

    # autoincrement 自動遞增（類似 IDENTITY(1,1)）
    partition_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 等價於
    # CREATE TABLE PARTITION (
    # partition_id INT PRIMARY KEY IDENTITY(1,1),
    # name NVARCHAR(255) NOT NULL
    # ); 
