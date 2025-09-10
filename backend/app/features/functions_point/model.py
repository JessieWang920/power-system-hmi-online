# backend/app/features/functions_points/model.py
from __future__ import annotations
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class FunctionsPoints(Base):
    """
    對應資料表 [FUNCTIONS_POINTS]
    """
    __tablename__ = "FUNCTIONS_POINTS"

    fu_point_id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    point_id    : Mapped[int] = mapped_column(Integer, ForeignKey("POINTS.point_id"))
    fu_formula_id:Mapped[int] = mapped_column(Integer, ForeignKey("FUNCTIONS_FORMULA.fu_formula_id"))
    sdi_id      : Mapped[int] = mapped_column(Integer, ForeignKey("SDI_LIST.sdi_id"))

    # ★ relationship 若要用可自行開啟
    # point      : Mapped["Points"]             = relationship(back_populates="functions_points")
    # formula    : Mapped["FunctionsFormula"]   = relationship()
