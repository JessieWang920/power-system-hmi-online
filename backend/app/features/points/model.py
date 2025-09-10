# backend\app\features\points\model.py
"""
CREATE TABLE [dbo].[POINTS](
[point_id] INT IDENTITY(1,1) NOT NULL,
[name] NVARCHAR(255) NOT NULL,
[partition_id] INT NOT NULL,
[di_id] INT NULL,
[ai_id] INT NULL,
[do_id] INT NULL,
[sdi_id] INT NULL,
CONSTRAINT [PK_POINTS] PRIMARY KEY CLUSTERED ([point_id] ASC)
);
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship,Mapped, mapped_column
from app.core.db import Base

class Points(Base):
    __tablename__ = "POINTS"

    point_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String(255), nullable=False)
    partition_id : Mapped[int] = mapped_column(Integer, nullable=False)
    di_id : Mapped[int] = mapped_column(Integer,ForeignKey("DI_LIST.di_id"), nullable=True)
    ai_id : Mapped[int] = mapped_column(Integer, nullable=True)
    do_id : Mapped[int] = mapped_column(Integer, nullable=True)
    sdi_id : Mapped[int] = mapped_column(Integer, nullable=True)
    # # ⏬ 關聯：一對多
    # do_list = relationship("DOList", back_populates="point")
    # elements = relationship("Element", back_populates="point")

    elements=relationship(
        "app.features.elements.model.Elements",
        back_populates="points",
        lazy="selectin",
        # cascade="all"#, delete-orphan",
    )

    ai_objects_text = relationship(
        "app.features.ai_objects_text.model.AIObjectsText",
          back_populates="points", 
          lazy="selectin"
        #   cascade="all"
          )

    di  = relationship(
        "app.features.di.model.DIList",
          back_populates="points", 
          lazy="selectin"
        #   cascade="all"
          )
