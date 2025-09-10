# backend/app/features/functions_formula/model.py
from __future__ import annotations
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class FunctionsFormula(Base):
    __tablename__ = "FUNCTIONS_FORMULA"

    fu_formula_id:       Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    formula_order:       Mapped[int]
    setValue:            Mapped[int | None]
    isTrue_operand_type: Mapped[int | None]
    isTrue:              Mapped[int | None]
    isFalse_operand_type:Mapped[int | None]
    isFalse:             Mapped[int | None]
    function_id:         Mapped[int] = mapped_column(Integer, ForeignKey("FUNCTIONS_LIST.function_id"))
    fu_operator_id:      Mapped[int | None] = mapped_column(Integer, ForeignKey("FUNCTIONS_OPERATOR.fu_operator_id"))


    functionlist= relationship("app.features.functions_list.model.FunctionsList", 
                                back_populates="formula", 
                                lazy="selectin")

    operator=relationship("app.features.functions_operator.model.FunctionsOperator",
                           lazy="selectin", back_populates="formula")



    # functionlist:Mapped["FunctionsList"]  = relationship("app.features.functions_list.model.FunctionsList", 
    #                             back_populates="formula", 
    #                             lazy="selectin")

    # operator:Mapped["FunctionsOperator"] =relationship("app.features.functions_operator.model.FunctionsOperator", lazy="selectin", back_populates="formulas")

    # function:  Mapped["FunctionsList"]      = relationship(back_populates="formulas")
    # operator:  Mapped["FunctionsOperator"] | None = relationship(back_populates="formulas")
    # points:    Mapped[list["FunctionsPoints"]] = relationship(back_populates="formula")