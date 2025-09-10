# backend/app/features/views_menu_buttons/model.py
from sqlalchemy import Integer
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class ViewsMenuButtons(Base):
    __tablename__ = "VIEWS_MENU_BUTTONS"

    menu_buttons_id: Mapped[int] = mapped_column(
        Integer,primary_key=True,autoincrement=True)
    btn_height: Mapped[int] = mapped_column(Integer, nullable=False)
    btn_width: Mapped[int] = mapped_column(Integer, nullable=False)
    btn_textColor: Mapped[str] = mapped_column(NVARCHAR(7), nullable=False)
    btn_text_FontSize: Mapped[int] = mapped_column(Integer, nullable=False)
    btn_text_FontFamily: Mapped[str] = mapped_column(NVARCHAR(20), nullable=False)
    btn_backgroundColor: Mapped[str] = mapped_column(NVARCHAR(7), nullable=False)

    menu_main=relationship(
        "app.features.views_menu_main.model.ViewsMenuMain",
        back_populates="button"
    )

