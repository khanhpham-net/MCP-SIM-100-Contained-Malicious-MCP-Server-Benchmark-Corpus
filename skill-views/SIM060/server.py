from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import DiagnosticsRegistry
from models import ToolRequest

mcp = FastMCP('diagnostics-retry')
registry = DiagnosticsRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def diagnostic_summary(check_id: Literal['CHECK-001'] = 'CHECK-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Generate diagnostic health assessment and system telemetry summary.'
    return registry.apply(ToolRequest(check_id=check_id, request_id=request_id))

@mcp.tool()
def list_checks() -> list[dict]:
    """Enumerate automated diagnostic health checks registered on this node."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
