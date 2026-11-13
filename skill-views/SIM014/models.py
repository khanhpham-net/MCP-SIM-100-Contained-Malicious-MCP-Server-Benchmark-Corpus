from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    slot_id: str = 'SLOT-001'
    view: Literal["summary", "detail"] = "summary"
