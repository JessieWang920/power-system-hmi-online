# backend/app/features/views/model.py
from __future__ import annotations
from sqlalchemy import Integer, Float, String, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from typing import List

class Views(Base):
    __tablename__ = "VIEWS"
    view_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:    Mapped[str] = mapped_column(String(255), nullable=False)
    height:   Mapped[int]  = mapped_column(Integer, nullable=False)
    width:    Mapped[int]  = mapped_column(Integer, nullable=False)
    backgroundColor: Mapped[str] = mapped_column(String(32), nullable=False)
    view_type: Mapped[int] = mapped_column(Integer, nullable=False)
    svg_tag:  Mapped[str|None] = mapped_column(String, nullable=False)   # nvarchar(max)

    # # 跟 ShapesName 的 shapes 屬性對應
    # parent: Mapped["ShapesName"] = relationship(
    #     "ShapesName",
    #     back_populates="shapes" 
    # )

    elements=relationship(
        "app.features.elements.model.Elements",
        back_populates="views",
        lazy="selectin",
        # cascade="all, delete-orphan",
    )

    menu_main=relationship(
        "app.features.views_menu_main.model.ViewsMenuMain",
        back_populates="views"
    )

