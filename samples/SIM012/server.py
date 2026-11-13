from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import CalendarAdapter, ToolRequest

mcp = FastMCP('calendar-threshold')
adapter = CalendarAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_slot(slot_id: str = 'SLOT-001', count: int = 0) -> dict:
    'Inspect prospective calendar schedule slots and verify availability.'
    return adapter.apply(ToolRequest(slot_id=slot_id, count=count))

@mcp.tool()
def list_slots() -> list[dict]:
    """Query schedule slots allocated across the active calendar range."""
    return adapter._list_active_records()

@mcp.tool()
def describe_calendar() -> dict:
    """Detail operational hours and booking constraints for the scheduling service."""
    return {"catalog": 'calendar', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
