# backend/app/features/shapes_name/model.py
from __future__ import annotations
from sqlalchemy import Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class ShapesName(Base):
    __tablename__ = "SHAPES_NAME"

    shape_name_id: Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:           Mapped[str]   = mapped_column(String(255), nullable=False)
    group_width:    Mapped[float] = mapped_column(Float, default=0)
    group_height:   Mapped[float] = mapped_column(Float, default=0)
    # group_x:        Mapped[float] = mapped_column(Float, default=0)
    group_y:        Mapped[float] = mapped_column(Float, default=0)
    view_id:        Mapped[int | None] = mapped_column(Integer, nullable=True)
    link_URL:       Mapped[str | None] = mapped_column(String(2000), nullable=True)
    svg_tag:        Mapped[str | None] = mapped_column(Text, nullable=True)

    # ← 只寫字串，不從 shapes.import Shape
    shapes = relationship(
        "app.features.shapes.model.Shapes",
        back_populates="shape_name",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
