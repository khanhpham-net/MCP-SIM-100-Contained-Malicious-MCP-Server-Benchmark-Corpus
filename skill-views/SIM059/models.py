from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    check_id: str = 'CHECK-001'
    view: Literal["summary", "detail"] = "summary"
