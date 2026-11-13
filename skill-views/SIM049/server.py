from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import MaintenanceService
from models import ToolRequest

mcp = FastMCP('maintenance-sequence')
service = MaintenanceService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_maintenance(plan_id: str = 'PLAN-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Evaluate scheduled service checklists and review maintenance items.'
    return service.apply(ToolRequest(plan_id=plan_id, view=view))

@mcp.tool()
def list_plans() -> list[dict]:
    """Retrieve scheduled maintenance plan identifiers awaiting execution."""
    return service._list_active_records()

@mcp.tool()
def describe_maintenance() -> dict:
    """Outline preventive maintenance schedules and service tier policies."""
    return {"catalog": 'maintenance', "view": "summary"}

@mcp.tool()
def validate_plan_id(plan_id: str = 'PLAN-001') -> dict:
    """Verify service plan reference code conforms to maintenance schema."""
    return service.validate_plan_id(plan_id)

@mcp.tool()
def export_maintenance_schema() -> dict:
    """Output preventive maintenance schedule specifications in JSON schema."""
    return service.export_maintenance_schema()

@mcp.tool()
def ping_maintenance_node() -> dict:
    """Verify connection availability to the maintenance scheduler service."""
    return service.ping_maintenance_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
