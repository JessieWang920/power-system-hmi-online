# backend/app/features/di/model.py
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class DIList(Base):
    __tablename__ = "DI_LIST"
    di_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    point_num: Mapped[int]= mapped_column(Integer, nullable=False)
    description: Mapped[str]= mapped_column(String(255), nullable=True)


    points = relationship(
        "app.features.points.model.Points",lazy="selectin", back_populates="di")
    