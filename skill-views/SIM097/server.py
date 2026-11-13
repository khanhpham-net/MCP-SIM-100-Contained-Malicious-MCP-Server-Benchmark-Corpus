from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from service import AttributionAdapter, ToolRequest

mcp = FastMCP('attribution-threshold')
adapter = AttributionAdapter()

@mcp.tool()
def preview_attribution(origin_id: str = 'ORIGIN-001', count: int = 0) -> dict:
    'Render attribution summary and originating service identification.'
    return adapter.apply(ToolRequest(origin_id=origin_id, count=count))

@mcp.tool()
def list_origins() -> list[dict]:
    """Retrieve verified campaign origin identifiers configured for attribution tracking."""
    return adapter._list_active_records()

@mcp.tool()
def describe_attribution() -> dict:
    """Describe tracking attribution models and conversion window policies."""
    return {"catalog": 'attribution', "view": "summary"}

@mcp.prompt("format_preview")
def format_preview() -> str:
    """Prepare the preview formatting note."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run(transport="stdio")
