from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    indicator_id: str = 'LED-001'
    view: Literal["summary", "detail"] = "summary"
