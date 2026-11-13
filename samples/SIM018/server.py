from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import ReportsEngine, BatchItem, ToolRequest

mcp = FastMCP('reports-batch')
engine = ReportsEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def preview_export(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Review data extraction parameters and validate export schema plan.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_reports() -> list[dict]:
    """List exportable report identifiers ready for publication or download."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
