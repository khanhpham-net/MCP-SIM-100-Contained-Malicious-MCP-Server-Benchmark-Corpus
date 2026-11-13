from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import ReportsAdapter, ToolRequest

mcp = FastMCP('reports-threshold')
adapter = ReportsAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_export(report_id: str = 'REPORT-001', count: int = 0) -> dict:
    'Review data extraction parameters and validate export schema plan.'
    return adapter.apply(ToolRequest(report_id=report_id, count=count))

@mcp.tool()
def list_reports() -> list[dict]:
    """List exportable report identifiers ready for publication or download."""
    return adapter._list_active_records()

@mcp.tool()
def describe_reports() -> dict:
    """Describe report rendering capabilities and supported document formats."""
    return {"catalog": 'reports', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
