from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import CalendarEngine, BatchItem, ToolRequest

mcp = FastMCP('calendar-batch')
engine = CalendarEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def preview_slot(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Inspect prospective calendar schedule slots and verify availability.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_slots() -> list[dict]:
    """Query schedule slots allocated across the active calendar range."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
