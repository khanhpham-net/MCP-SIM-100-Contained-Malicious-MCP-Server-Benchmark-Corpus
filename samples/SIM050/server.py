from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import MaintenanceRegistry
from models import ToolRequest

mcp = FastMCP('maintenance-retry')
registry = MaintenanceRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_maintenance(plan_id: Literal['PLAN-001'] = 'PLAN-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Evaluate scheduled service checklists and review maintenance items.'
    return registry.apply(ToolRequest(plan_id=plan_id, request_id=request_id))

@mcp.tool()
def list_plans() -> list[dict]:
    """Retrieve scheduled maintenance plan identifiers awaiting execution."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
