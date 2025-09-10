# backend/app/features/ai_objects_text/model.py
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class AIObjectsText(Base):
    __tablename__ = "AI_OBJECTS_TEXT"

    ai_objectText_id  : Mapped[int]= mapped_column(Integer, primary_key=True, autoincrement=True)
    name              : Mapped[str] = mapped_column(String(255), nullable=True)
    font_family       : Mapped[str] = mapped_column(String(100), nullable=True)
    font_style        : Mapped[str] = mapped_column(String(100), nullable=True)
    font_size         : Mapped[int]= mapped_column(Integer, nullable=True)
    text              : Mapped[str] = mapped_column(String(10),   nullable=True)
    font_color        : Mapped[str] = mapped_column(String(7), nullable=True)
    point_id          :Mapped[int] = mapped_column(Integer, ForeignKey("POINTS.point_id"),nullable=True)
    unit              : Mapped[str] = mapped_column(String(7), nullable=True)

    points = relationship(
        "app.features.points.model.Points",lazy="selectin", back_populates="ai_objects_text")
    

