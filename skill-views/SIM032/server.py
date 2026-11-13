from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import IndicatorsAdapter, ToolRequest

mcp = FastMCP('indicators-threshold')
adapter = IndicatorsAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def check_indicator(indicator_id: str = 'LED-001', count: int = 0) -> dict:
    'Poll bus communication channel and verify indicator subsystem status.'
    return adapter.apply(ToolRequest(indicator_id=indicator_id, count=count))

@mcp.tool()
def list_indicators() -> list[dict]:
    """Enumerate operational status indicators across managed subsystems."""
    return adapter._list_active_records()

@mcp.tool()
def describe_indicators() -> dict:
    """Outline bus signal definitions and visual alert thresholds."""
    return {"catalog": 'indicators', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
