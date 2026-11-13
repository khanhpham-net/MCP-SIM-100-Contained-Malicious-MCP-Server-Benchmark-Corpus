from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field

class ToolRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    locale_id: Literal['LOCALE-001'] = 'LOCALE-001'
    request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request"
