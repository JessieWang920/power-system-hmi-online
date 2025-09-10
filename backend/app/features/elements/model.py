# backend/app/features/elements/model.py
from __future__ import annotations
from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Elements(Base):
    __tablename__ = "ELEMENTS"

    elem_id:   Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    # point_id:  Mapped[int | None] = mapped_column(Integer, nullable=True)
    point_id: Mapped[int] = mapped_column(Integer, ForeignKey("POINTS.point_id"), nullable=True)
    name:      Mapped[str]  = mapped_column(String(255), nullable=False)
    view_id:   Mapped[int | None] = mapped_column(Integer, ForeignKey("VIEWS.view_id"), nullable=True)
    link_URL:  Mapped[str | None] = mapped_column(String(2000), nullable=True)
    isLock:    Mapped[bool] = mapped_column(Boolean, default=False)

    views :Mapped["Views"] = relationship("app.features.views.model.Views",
                           back_populates="elements", 
                           lazy="selectin")
    points :Mapped["Points"] = relationship("app.features.points.model.Points", 
                          back_populates="elements", 
                          lazy="selectin")
