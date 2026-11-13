from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import IndicatorsService
from models import ToolRequest

mcp = FastMCP('indicators-sequence')
service = IndicatorsService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def check_indicator(indicator_id: str = 'LED-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Poll bus communication channel and verify indicator subsystem status.'
    return service.apply(ToolRequest(indicator_id=indicator_id, view=view))

@mcp.tool()
def list_indicators() -> list[dict]:
    """Enumerate operational status indicators across managed subsystems."""
    return service._list_active_records()

@mcp.tool()
def describe_indicators() -> dict:
    """Outline bus signal definitions and visual alert thresholds."""
    return {"catalog": 'indicators', "view": "summary"}

@mcp.tool()
def validate_indicator_id(indicator_id: str = 'LED-001') -> dict:
    """Check hardware indicator identifier against the registry map."""
    return service.validate_indicator_id(indicator_id)

@mcp.tool()
def export_indicators_schema() -> dict:
    """Output bus monitor state specifications for diagnostic telemetry."""
    return service.export_indicators_schema()

@mcp.tool()
def ping_indicators_node() -> dict:
    """Test network roundtrip time to the indicator signaling bus."""
    return service.ping_indicators_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
