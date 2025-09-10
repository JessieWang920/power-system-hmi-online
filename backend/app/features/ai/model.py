from sqlalchemy import Integer, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class AIList(Base):
    __tablename__ = "AI_LIST"

    ai_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataType_id: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_min: Mapped[float] = mapped_column(Float, nullable=True)
    ai_max: Mapped[float] = mapped_column(Float, nullable=True)
