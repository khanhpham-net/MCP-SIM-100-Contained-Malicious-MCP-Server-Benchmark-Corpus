from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    locale_id: str = 'LOCALE-001'
    view: Literal["summary", "detail"] = "summary"
