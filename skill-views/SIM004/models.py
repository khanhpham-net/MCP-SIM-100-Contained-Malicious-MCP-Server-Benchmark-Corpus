from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    sku: str = 'SKU-001'
    view: Literal["summary", "detail"] = "summary"
