# backend/app/features/elements_shape/model.py

from sqlalchemy import Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base  # 或你專案中 Base 的 import 路徑

class ElementsShapes(Base):
    __tablename__ = "ELEMENTS_SHAPES"

    elem_shapes_id: Mapped[int] = mapped_column(Integer,primary_key=True
                                                ,autoincrement=True,nullable=False)
    elem_id: Mapped[int] = mapped_column(Integer,ForeignKey("ELEMENTS.elem_id"),nullable=False)
    status: Mapped[int] = mapped_column(Integer,nullable=False)
    statu_default: Mapped[bool] = mapped_column(Boolean,nullable=False)
    shape_name_id: Mapped[int] = mapped_column(Integer
                                               ,ForeignKey("SHAPES_NAME.shape_name_id"),nullable=True)
