# backend/app/features/functions_list/model.py
from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from typing import List

class FunctionsList(Base):
    __tablename__ = "FUNCTIONS_LIST"

    function_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:        Mapped[str] = mapped_column("name", String(255), nullable=False)
    parameters:  Mapped[int] = mapped_column(Integer, nullable=True)

    # # 關聯到子公式
    formula = relationship("app.features.functions_formula.model.FunctionsFormula",
        back_populates="functionlist",
          lazy="selectin", 
        # cascade="all, delete-orphan"
    )


    # formula : Mapped[List["FunctionsFormula"]] = relationship("app.features.functions_formula.model.FunctionsFormula",
    #     back_populates="functionlist", lazy="selectin", 
    #     # cascade="all, delete-orphan"
    # )