from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import CalibrationService
from models import ToolRequest

mcp = FastMCP('calibration-sequence')
service = CalibrationService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def inspect_calibration(device_id: str = 'DEVICE-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Inspect system operating parameters and active calibration baseline.'
    return service.apply(ToolRequest(device_id=device_id, view=view))

@mcp.tool()
def list_devices() -> list[dict]:
    """List hardware device profiles scheduled for calibration checks."""
    return service._list_active_records()

@mcp.tool()
def describe_calibration() -> dict:
    """Summarize instrumentation tolerance bands and inspection intervals."""
    return {"catalog": 'calibration', "view": "summary"}

@mcp.tool()
def validate_device_id(device_id: str = 'DEVICE-001') -> dict:
    """Verify device calibration identifier conforms to instrument specs."""
    return service.validate_device_id(device_id)

@mcp.tool()
def export_calibration_schema() -> dict:
    """Export device calibration measurement schema for quality assurance."""
    return service.export_calibration_schema()

@mcp.tool()
def ping_calibration_node() -> dict:
    """Probe operational status of the device calibration controller."""
    return service.ping_calibration_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
