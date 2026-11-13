from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    plan_id: str = 'PLAN-001'
    view: Literal["summary", "detail"] = "summary"
