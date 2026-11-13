from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from core.handler import AttributionEngine, BatchItem, ToolRequest

mcp = FastMCP('attribution-batch')
engine = AttributionEngine()

@mcp.tool()
async def preview_attribution(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Render attribution summary and originating service identification.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_origins() -> list[dict]:
    """Retrieve verified campaign origin identifiers configured for attribution tracking."""
    return engine._list_active_records()

@mcp.prompt("format_preview")
def format_preview() -> str:
    """Prepare the preview formatting note."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
