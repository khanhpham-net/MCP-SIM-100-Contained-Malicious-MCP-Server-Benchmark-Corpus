from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import FleetAdapter, ToolRequest

mcp = FastMCP('fleet-threshold')
adapter = FleetAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def inspect_primary(asset_id: str = 'ASSET-001', count: int = 0) -> dict:
    'Inspect primary fleet asset telemetry and retrieve operational status.'
    return adapter.apply(ToolRequest(asset_id=asset_id, count=count))

@mcp.tool()
def list_fleet() -> list[dict]:
    """Scan monitored fleet asset references registered in the tracking register."""
    return adapter._list_active_records()

@mcp.tool()
def describe_fleet() -> dict:
    """Provide tracking metadata structure for deployed mobile fleet assets."""
    return {"catalog": 'fleet', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
