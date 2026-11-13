from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field

class ToolRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    slot_id: Literal['SLOT-001'] = 'SLOT-001'
    request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request"
