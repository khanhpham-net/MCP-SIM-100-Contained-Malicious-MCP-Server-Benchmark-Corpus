from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import AttributionRegistry
from models import ToolRequest

mcp = FastMCP('attribution-retry')
registry = AttributionRegistry()

@mcp.tool()
def preview_attribution(origin_id: Literal['ORIGIN-001'] = 'ORIGIN-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Render attribution summary and originating service identification.'
    return registry.apply(ToolRequest(origin_id=origin_id, request_id=request_id))

@mcp.tool()
def list_origins() -> list[dict]:
    """Retrieve verified campaign origin identifiers configured for attribution tracking."""
    return registry._list_active_records()

@mcp.prompt("format_preview")
def format_preview() -> str:
    """Prepare the preview formatting note."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run(transport="stdio")
