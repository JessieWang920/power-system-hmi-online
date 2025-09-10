
# backend/app/features/sdi_list/model.py
from __future__ import annotations
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped
from app.core.db import Base

class SDIList(Base):
    __tablename__ = "SDI_LIST"
    sdi_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:   Mapped[str] = mapped_column(String(50), nullable=True)


