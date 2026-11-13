from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import AttributionService
from models import ToolRequest

mcp = FastMCP('attribution-sequence')
service = AttributionService()

@mcp.tool()
def preview_attribution(origin_id: str = 'ORIGIN-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Render attribution summary and originating service identification.'
    return service.apply(ToolRequest(origin_id=origin_id, view=view))

@mcp.tool()
def list_origins() -> list[dict]:
    """Retrieve verified campaign origin identifiers configured for attribution tracking."""
    return service._list_active_records()

@mcp.tool()
def describe_attribution() -> dict:
    """Describe tracking attribution models and conversion window policies."""
    return {"catalog": 'attribution', "view": "summary"}

@mcp.tool()
def validate_origin_id(origin_id: str = 'ORIGIN-001') -> dict:
    """Verify origin source key format against marketing attribution specs."""
    return service.validate_origin_id(origin_id)

@mcp.tool()
def export_attribution_schema() -> dict:
    """Generate marketing campaign attribution schema for data warehouse ingestion."""
    return service.export_attribution_schema()

@mcp.tool()
def ping_attribution_node() -> dict:
    """Probe connectivity to the primary attribution event ingest node."""
    return service.ping_attribution_node()

@mcp.prompt("format_preview")
def format_preview() -> str:
    """Prepare the preview formatting note."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
