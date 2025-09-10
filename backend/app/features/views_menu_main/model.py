# backend/app/features/views_menu_main/model.py
from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

class ViewsMenuMain(Base):
    __tablename__ = "VIEWS_MENU_MAIN"

    menu_main_id:  Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    main_order:    Mapped[int]   = mapped_column(Integer, nullable=False )
    view_id:       Mapped[int]   = mapped_column(Integer, ForeignKey("VIEWS.view_id"), nullable=False)
    name:          Mapped[str]   = mapped_column(String(20), nullable=False)
    menu_buttons_id: Mapped[int] = mapped_column(Integer, 
                                                 ForeignKey("VIEWS_MENU_BUTTONS.menu_buttons_id"), 
                                                 nullable=False)
    link_URL:      Mapped[str]   = mapped_column(String(2000), nullable=True)
    isMain:        Mapped[bool]  = mapped_column(Boolean, nullable=True)

    button = relationship(
        "app.features.views_menu_buttons.model.ViewsMenuButtons", 
        back_populates="menu_main",
        lazy="selectin")
    
    views = relationship(
        "app.features.views.model.Views", 
        back_populates="menu_main",
        lazy="selectin",
        # cascade="all, delete-orphan",
        # uselist=False    # ← 保證一對一回傳單一 Views 實例
        )
    
