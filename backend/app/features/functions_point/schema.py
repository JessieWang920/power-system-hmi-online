# backend/app/features/functions_points/schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# ── 基底共用 ──────────────────────────────────────────
class _FPBase(BaseModel):
    sdi_id       : Optional[int]
    point_id     : Optional[int]
    fu_formula_id: Optional[int]

# ── Create / Update ─────────────────────────────────
class FPCreate(_FPBase):          
    pass
class FPUpdate(_FPBase):
    fu_point_id: int

# ── Delete ─────────────────────────────────────────
class FPDelete(BaseModel):
    fu_point_id: int

# ── 回傳 (POST / PUT) ───────────────────────────────
class FPResp(_FPBase):
    fu_point_id: int
    model_config = ConfigDict(from_attributes=True)

# ── GET?sdi_id= 的詳列 ───────────────────────────────
class FPDetail(BaseModel):
    fu_point_id              : int
    fu_sdi_id                : int
    formula_order            : int | None
    function_id              : int | None
    function_name            : str | None
    fu_sdi_point_name        : str | None
    fu_sdi_partition_id      : int | None
    fu_sdi_partition_name    : str | None
    fu_point_point_id        : int | None
    fu_point_point_name      : str | None
    fu_point_partition_id    : int | None
    fu_point_partition_name  : str | None
    fu_point_ai_id           : int | None
    fu_point_di_id           : int | None
