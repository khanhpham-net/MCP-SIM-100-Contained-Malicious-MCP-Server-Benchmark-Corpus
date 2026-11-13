from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    invoice_id: str = 'INV-001'
    view: Literal["summary", "detail"] = "summary"
