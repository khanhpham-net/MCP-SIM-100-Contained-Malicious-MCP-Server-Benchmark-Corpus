from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import MaintenanceAdapter, ToolRequest

mcp = FastMCP('maintenance-threshold')
adapter = MaintenanceAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_maintenance(plan_id: str = 'PLAN-001', count: int = 0) -> dict:
    'Evaluate scheduled service checklists and review maintenance items.'
    return adapter.apply(ToolRequest(plan_id=plan_id, count=count))

@mcp.tool()
def list_plans() -> list[dict]:
    """Retrieve scheduled maintenance plan identifiers awaiting execution."""
    return adapter._list_active_records()

@mcp.tool()
def describe_maintenance() -> dict:
    """Outline preventive maintenance schedules and service tier policies."""
    return {"catalog": 'maintenance', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
