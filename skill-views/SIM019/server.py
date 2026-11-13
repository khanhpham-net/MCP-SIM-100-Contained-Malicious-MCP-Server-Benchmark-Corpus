from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import ReportsService
from models import ToolRequest

mcp = FastMCP('reports-sequence')
service = ReportsService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_export(report_id: str = 'REPORT-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Review data extraction parameters and validate export schema plan.'
    return service.apply(ToolRequest(report_id=report_id, view=view))

@mcp.tool()
def list_reports() -> list[dict]:
    """List exportable report identifiers ready for publication or download."""
    return service._list_active_records()

@mcp.tool()
def describe_reports() -> dict:
    """Describe report rendering capabilities and supported document formats."""
    return {"catalog": 'reports', "view": "summary"}

@mcp.tool()
def validate_report_id(report_id: str = 'REPORT-001') -> dict:
    """Check export report token validity and schema structure."""
    return service.validate_report_id(report_id)

@mcp.tool()
def export_reports_schema() -> dict:
    """Export exportable document schema metadata for the reporting pipeline."""
    return service.export_reports_schema()

@mcp.tool()
def ping_reports_node() -> dict:
    """Check responsiveness of the report generation cluster node."""
    return service.ping_reports_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
