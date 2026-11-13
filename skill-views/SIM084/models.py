from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    card_id: str = 'CARD-001'
    view: Literal["summary", "detail"] = "summary"
