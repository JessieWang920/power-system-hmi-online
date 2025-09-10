from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ---------- 共用欄位 ----------
class _BaseSide(BaseModel):
    side_order:      Optional[int] = None
    view_id:         Optional[int] = None
    name:            Optional[str] = None
    menu_buttons_id: Optional[int] = None
    menu_main_id:    Optional[int] = None
    link_URL:        Optional[str] = None


# ---------- POST ----------
class SideCreate(_BaseSide):
    """
    建立 VIEWS_MENU_SIDE 時使用的 Payload
    """
    menu_main_id: int  # 必填


class SideCreatedResp(BaseModel):
    """
    POST 回傳：僅需 menu_side_id
    """
    menu_side_id: int
#------------ DELETE ------------
class SideDelete(BaseModel):
    menu_side_id: int

# ---------- PUT ----------
class SideUpdate(BaseModel):
    """
    更新用：必須帶 menu_side_id，其餘欄位可選
    """
    menu_side_id: int
    side_order:      Optional[int] = None
    view_id:         Optional[int] = None
    name:            Optional[str] = None
    menu_buttons_id: Optional[int] = None
    link_URL:        Optional[str] = None


class SideResp(_BaseSide):
    """
    PUT 成功回傳（單列，包成 List 讓前端好統一）
    """
    menu_side_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------- GET ----------
class SideDetailResp(SideResp):
    """
    GET 詳細回傳（含 JOIN 兩張表的欄位）
    """
    # 按鈕樣式
    btn_height:            Optional[int]   = None
    btn_width:             Optional[int]   = None
    btn_textColor:         Optional[str]   = None
    btn_text_FontSize:     Optional[int]   = None
    btn_text_FontFamily:   Optional[str]   = None
    btn_backgroundColor:   Optional[str]   = None
    # View 額外欄位
    view_name:             Optional[str]   = None
    view_height:           Optional[int]   = None
    view_width:            Optional[int]   = None
    view_backgroundColor:  Optional[str]   = None
    view_view_type:        Optional[int]   = Field(None, alias="view_view_type")
    view_svg_tag:          Optional[str]   = None
