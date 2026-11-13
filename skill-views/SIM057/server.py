from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import DiagnosticsAdapter, ToolRequest

mcp = FastMCP('diagnostics-threshold')
adapter = DiagnosticsAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def diagnostic_summary(check_id: str = 'CHECK-001', count: int = 0) -> dict:
    'Generate diagnostic health assessment and system telemetry summary.'
    return adapter.apply(ToolRequest(check_id=check_id, count=count))

@mcp.tool()
def list_checks() -> list[dict]:
    """Enumerate automated diagnostic health checks registered on this node."""
    return adapter._list_active_records()

@mcp.tool()
def describe_diagnostics() -> dict:
    """Summarize self-test diagnostic parameters and monitoring criteria."""
    return {"catalog": 'diagnostics', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
