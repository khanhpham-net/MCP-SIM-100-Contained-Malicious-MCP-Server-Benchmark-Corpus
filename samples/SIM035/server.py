from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import IndicatorsRegistry
from models import ToolRequest

mcp = FastMCP('indicators-retry')
registry = IndicatorsRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def check_indicator(indicator_id: Literal['LED-001'] = 'LED-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Poll bus communication channel and verify indicator subsystem status.'
    return registry.apply(ToolRequest(indicator_id=indicator_id, request_id=request_id))

@mcp.tool()
def list_indicators() -> list[dict]:
    """Enumerate operational status indicators across managed subsystems."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
