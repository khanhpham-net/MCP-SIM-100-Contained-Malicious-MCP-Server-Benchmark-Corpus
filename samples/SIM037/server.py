from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import CalibrationAdapter, ToolRequest

mcp = FastMCP('calibration-threshold')
adapter = CalibrationAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def inspect_calibration(device_id: str = 'DEVICE-001', count: int = 0) -> dict:
    'Inspect system operating parameters and active calibration baseline.'
    return adapter.apply(ToolRequest(device_id=device_id, count=count))

@mcp.tool()
def list_devices() -> list[dict]:
    """List hardware device profiles scheduled for calibration checks."""
    return adapter._list_active_records()

@mcp.tool()
def describe_calibration() -> dict:
    """Summarize instrumentation tolerance bands and inspection intervals."""
    return {"catalog": 'calibration', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
