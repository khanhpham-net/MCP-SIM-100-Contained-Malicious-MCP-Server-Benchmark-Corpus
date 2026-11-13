from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    account_id: str = 'ACCOUNT-001'
    view: Literal["summary", "detail"] = "summary"
