# backend/app/features/functions_operator/model.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class FunctionsOperator(Base):
    __tablename__ = "FUNCTIONS_OPERATOR"

    fu_operator_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]          = mapped_column(String(50), nullable=False, comment="運算子名稱 (=, <, >, …)")


    # 關聯到子公式
    formula = relationship("app.features.functions_formula.model.FunctionsFormula",
        back_populates="operator",
          lazy="selectin", 
        # cascade="all, delete-orphan"
    )

