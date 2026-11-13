from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    contact_id: str = 'CONTACT-001'
    view: Literal["summary", "detail"] = "summary"
