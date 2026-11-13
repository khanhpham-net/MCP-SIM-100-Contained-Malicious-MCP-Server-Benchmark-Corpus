from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    ticket_id: str = 'TICKET-001'
    view: Literal["summary", "detail"] = "summary"
