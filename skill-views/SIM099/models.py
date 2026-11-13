from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    origin_id: str = 'ORIGIN-001'
    view: Literal["summary", "detail"] = "summary"
