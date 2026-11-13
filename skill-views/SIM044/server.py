from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import FleetService
from models import ToolRequest

mcp = FastMCP('fleet-sequence')
service = FleetService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def inspect_primary(asset_id: str = 'ASSET-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Inspect primary fleet asset telemetry and retrieve operational status.'
    return service.apply(ToolRequest(asset_id=asset_id, view=view))

@mcp.tool()
def list_fleet() -> list[dict]:
    """Scan monitored fleet asset references registered in the tracking register."""
    return service._list_active_records()

@mcp.tool()
def describe_fleet() -> dict:
    """Provide tracking metadata structure for deployed mobile fleet assets."""
    return {"catalog": 'fleet', "view": "summary"}

@mcp.tool()
def validate_asset_id(asset_id: str = 'ASSET-001') -> dict:
    """Validate asset tracking identifier against fleet inventory standards."""
    return service.validate_asset_id(asset_id)

@mcp.tool()
def export_fleet_schema() -> dict:
    """Generate asset telematics schema definitions for fleet monitoring."""
    return service.export_fleet_schema()

@mcp.tool()
def ping_fleet_node() -> dict:
    """Send connectivity check to the primary fleet telematics gateway."""
    return service.ping_fleet_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
