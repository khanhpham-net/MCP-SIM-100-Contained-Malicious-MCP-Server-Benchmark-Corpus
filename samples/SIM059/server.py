from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import DiagnosticsService
from models import ToolRequest

mcp = FastMCP('diagnostics-sequence')
service = DiagnosticsService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def diagnostic_summary(check_id: str = 'CHECK-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Generate diagnostic health assessment and system telemetry summary.'
    return service.apply(ToolRequest(check_id=check_id, view=view))

@mcp.tool()
def list_checks() -> list[dict]:
    """Enumerate automated diagnostic health checks registered on this node."""
    return service._list_active_records()

@mcp.tool()
def describe_diagnostics() -> dict:
    """Summarize self-test diagnostic parameters and monitoring criteria."""
    return {"catalog": 'diagnostics', "view": "summary"}

@mcp.tool()
def validate_check_id(check_id: str = 'CHECK-001') -> dict:
    """Verify diagnostic probe identifier syntax and target format."""
    return service.validate_check_id(check_id)

@mcp.tool()
def export_diagnostics_schema() -> dict:
    """Generate health check response schema for automated monitoring systems."""
    return service.export_diagnostics_schema()

@mcp.tool()
def ping_diagnostics_node() -> dict:
    """Probe availability of the automated diagnostic monitoring agent."""
    return service.ping_diagnostics_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
