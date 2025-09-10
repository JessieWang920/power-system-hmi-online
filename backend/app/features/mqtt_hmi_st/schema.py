from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# ──────── Response ────────
class _Content(BaseModel):
    TagName: str
    Value:   float
    Time:    datetime
    Quality: int

class MqttStResp(BaseModel):
    Type:    str = Field("ST", serialization_alias="Type")
    Content: _Content

    model_config = ConfigDict(from_attributes=True)
