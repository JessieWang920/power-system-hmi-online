
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
from sqlalchemy import Integer, String, Float

class AiDataTypeList(Base):
    __tablename__ = "AI_DATATYPE_LIST"

    data_type_id:   Mapped[int] = mapped_column("dataType_id", Integer, primary_key=True, autoincrement=True, nullable=False)
    input_max:      Mapped[float] = mapped_column("inputMax", Float, nullable=True)
    output_max:     Mapped[float] = mapped_column("ouptMax", Float, nullable=True)
    name:           Mapped[str] = mapped_column(String(255), nullable=True)    
    input_min:      Mapped[float] = mapped_column("inputMin", Float, nullable=True)
    output_min:     Mapped[float] = mapped_column("outputMin", Float, nullable=True)
