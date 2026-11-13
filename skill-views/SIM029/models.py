from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    meter_id: str = 'METER-001'
    view: Literal["summary", "detail"] = "summary"
