from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class ViewShape(Base):
    __tablename__ = "VIEW_SHAPES"

    view_shape_id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True,nullable=False)
    view_shape_order: Mapped[int] = mapped_column(Integer,nullable=False)
    x: Mapped[int] = mapped_column(Integer,nullable=False)
    y: Mapped[int] = mapped_column(Integer,nullable=False)
    view_id: Mapped[int] = mapped_column(Integer, ForeignKey("VIEWS.view_id"),nullable=False)
    elem_id: Mapped[int] = mapped_column(Integer,ForeignKey("ELEMENTS.elem_id"),nullable=True)
    shape_name_id: Mapped[int] = mapped_column( Integer,ForeignKey("SHAPES_NAME.shape_name_id"),nullable=True)
    ai_objectText_id: Mapped[int] = mapped_column( Integer,ForeignKey("AI_OBJECTS_TEXT.ai_objectText_id"),nullable=True)


    view   = relationship("app.features.views.model.Views",        lazy="selectin")
    elem   = relationship("app.features.elements.model.Elements",  lazy="selectin")
    sname  = relationship("app.features.shapes_name.model.ShapesName", lazy="selectin")