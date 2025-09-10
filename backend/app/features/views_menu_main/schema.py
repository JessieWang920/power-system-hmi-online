# backend/app/features/views_menu_main/schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

# ────────── 共用欄位 ──────────
class _Base(BaseModel):
    main_order:      int
    view_id:         int
    name:            str
    menu_buttons_id: int
    link_URL:        Optional[str]
    isMain:          Optional[int]

# ────────── Create ──────────
class MenuMainCreate(_Base):
    pass

class MenuMainResp(BaseModel):
    menu_main_id: int
    
    
# ────────── Update / Delete ──────────
class MenuMainUpdate(_Base):
    menu_main_id: int
    model_config = ConfigDict(from_attributes=True)

class MenuMainDelete(BaseModel):
    menu_main_id: int

# ────────── Get ──────────
class MenuMainListResp(_Base):
    menu_main_id: int
    btn_height: int
    btn_width: int
    btn_textColor: str
    btn_text_FontSize: int
    btn_text_FontFamily: str
    btn_backgroundColor: str
    view_name: str
    view_height: int
    view_width: int
    view_backgroundColor: str
    view_view_type: int
    view_svg_tag: Optional[str] = None

