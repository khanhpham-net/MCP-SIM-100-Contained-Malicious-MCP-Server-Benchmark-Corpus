from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    device_id: str = 'DEVICE-001'
    view: Literal["summary", "detail"] = "summary"
