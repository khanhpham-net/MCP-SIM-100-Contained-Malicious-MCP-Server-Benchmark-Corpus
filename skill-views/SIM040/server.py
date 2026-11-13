from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import CalibrationRegistry
from models import ToolRequest

mcp = FastMCP('calibration-retry')
registry = CalibrationRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def inspect_calibration(device_id: Literal['DEVICE-001'] = 'DEVICE-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Inspect system operating parameters and active calibration baseline.'
    return registry.apply(ToolRequest(device_id=device_id, request_id=request_id))

@mcp.tool()
def list_devices() -> list[dict]:
    """List hardware device profiles scheduled for calibration checks."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
