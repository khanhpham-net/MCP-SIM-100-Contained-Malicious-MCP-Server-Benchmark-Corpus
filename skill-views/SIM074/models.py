from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    profile_id: str = 'PROFILE-001'
    view: Literal["summary", "detail"] = "summary"
