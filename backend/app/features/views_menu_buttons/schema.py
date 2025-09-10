# backend/app/features/views_menu_buttons/schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class _Base(BaseModel):
    btn_height: int = Field(default=100, ge=1)
    btn_width:  int = Field(default=100, ge=1)
    btn_textColor:   str = "#FFFFFF"
    btn_text_FontSize: int = Field(default=20, ge=6, le=72)
    btn_text_FontFamily: str = "Microsoft JhenggHei"
    btn_backgroundColor: str = "#000000"

# ── Create ──
class VMBCreate(_Base): pass

# ── Update ──
class VMBUpdate(_Base):
    menu_buttons_id: int

# ── Delete ──
class VMBDelete(BaseModel):
    menu_buttons_id: int

# ── Response ──
class VMBResp(_Base):
    menu_buttons_id: int
    model_config = ConfigDict(from_attributes=True)
