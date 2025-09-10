# backend/app/features/shapes/model.py
from __future__ import annotations
from sqlalchemy import Integer, Float, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Shapes(Base):
    __tablename__ = "SHAPES"

    shape_id:       Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    shape_name_id:  Mapped[int]   = mapped_column(ForeignKey("SHAPES_NAME.shape_name_id"), nullable=False, index=True)
    shape_type:     Mapped[int]   = mapped_column(Integer)
    x:              Mapped[float] = mapped_column(Float)
    y:              Mapped[float] = mapped_column(Float)
    zoom:           Mapped[float] = mapped_column(Float)
    is_popup:       Mapped[bool]  = mapped_column(Boolean, default=False)
    is_shine:       Mapped[bool]  = mapped_column(Boolean, default=False)
    tooltips:       Mapped[str|None] = mapped_column(String(255), nullable=True)
    width:          Mapped[float] = mapped_column(Float)
    height:         Mapped[float] = mapped_column(Float)
    fill_color:     Mapped[str|None] = mapped_column(String(50), nullable=True)
    fill_style:     Mapped[str|None] = mapped_column(String(50), nullable=True)
    border_color:   Mapped[str|None] = mapped_column(String(50), nullable=True)
    border_width:   Mapped[int]   = mapped_column(Integer)
    angle:          Mapped[int]   = mapped_column(Integer)
    group_order:    Mapped[int]   = mapped_column(Integer)

    # ← 只寫字串，不從 shapes_name.import ShapeName
    shape_name = relationship(
        "app.features.shapes_name.model.ShapesName",
        back_populates="shapes",
        lazy="selectin",
    )
