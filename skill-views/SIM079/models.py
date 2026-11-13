from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    palette_id: str = 'PALETTE-001'
    view: Literal["summary", "detail"] = "summary"
