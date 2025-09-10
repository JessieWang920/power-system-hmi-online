from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ViewsMenuSide(Base):
    __tablename__ = "VIEWS_MENU_SIDE"

    menu_side_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    side_order:   Mapped[int]
    view_id:      Mapped[int | None]
    name:         Mapped[str]  = mapped_column(String(50))
    menu_buttons_id: Mapped[int]
    menu_main_id:    Mapped[int]
    link_URL:     Mapped[str | None] = mapped_column(String(2000))
