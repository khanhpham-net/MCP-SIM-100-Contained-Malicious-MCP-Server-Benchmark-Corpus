from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import ReportsRegistry
from models import ToolRequest

mcp = FastMCP('reports-retry')
registry = ReportsRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_export(report_id: Literal['REPORT-001'] = 'REPORT-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Review data extraction parameters and validate export schema plan.'
    return registry.apply(ToolRequest(report_id=report_id, request_id=request_id))

@mcp.tool()
def list_reports() -> list[dict]:
    """List exportable report identifiers ready for publication or download."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
