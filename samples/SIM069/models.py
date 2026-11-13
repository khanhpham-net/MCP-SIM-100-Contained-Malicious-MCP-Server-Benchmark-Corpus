from typing import Annotated, Literal
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    topic_id: str = 'TOPIC-001'
    view: Literal["summary", "detail"] = "summary"
