from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from core.handler import CatalogEngine, BatchItem, ToolRequest
from core.handler import ANNOTATION_NOTE

mcp = FastMCP('catalog-batch')
engine = CatalogEngine()

@mcp.tool()
async def preview_order(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Display catalog items according to configured presentation order.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_collections() -> list[dict]:
    """List curated collection records currently indexed in the store catalog."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
