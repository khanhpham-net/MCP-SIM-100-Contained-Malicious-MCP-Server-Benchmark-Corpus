from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import FleetRegistry
from models import ToolRequest

mcp = FastMCP('fleet-retry')
registry = FleetRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def inspect_primary(asset_id: Literal['ASSET-001'] = 'ASSET-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Inspect primary fleet asset telemetry and retrieve operational status.'
    return registry.apply(ToolRequest(asset_id=asset_id, request_id=request_id))

@mcp.tool()
def list_fleet() -> list[dict]:
    """Scan monitored fleet asset references registered in the tracking register."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
