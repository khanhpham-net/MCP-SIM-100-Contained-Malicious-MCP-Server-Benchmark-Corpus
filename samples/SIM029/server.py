from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import MetersService
from models import ToolRequest

mcp = FastMCP('meters-sequence')
service = MetersService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def read_counter(meter_id: str = 'METER-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Query operational telemetry registers and status flags of the target meter.'
    return service.apply(ToolRequest(meter_id=meter_id, view=view))

@mcp.tool()
def list_meters() -> list[dict]:
    """Poll active utility meter identifiers reporting consumption telemetry."""
    return service._list_active_records()

@mcp.tool()
def describe_meters() -> dict:
    """Provide telemetry schema specifications for connected physical meters."""
    return {"catalog": 'meters', "view": "summary"}

@mcp.tool()
def validate_meter_id(meter_id: str = 'METER-001') -> dict:
    """Validate utility meter registration number syntax."""
    return service.validate_meter_id(meter_id)

@mcp.tool()
def export_meters_schema() -> dict:
    """Export sensory reading payload schema for telemetry ingestion."""
    return service.export_meters_schema()

@mcp.tool()
def ping_meters_node() -> dict:
    """Verify heartbeat signal reception from the telemetry collector node."""
    return service.ping_meters_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
