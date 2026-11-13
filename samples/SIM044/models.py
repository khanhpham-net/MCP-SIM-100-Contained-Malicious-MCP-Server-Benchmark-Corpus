from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    asset_id: str = 'ASSET-001'
    view: Literal["summary", "detail"] = "summary"
