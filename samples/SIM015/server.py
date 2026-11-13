from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import CalendarRegistry
from models import ToolRequest

mcp = FastMCP('calendar-retry')
registry = CalendarRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_slot(slot_id: Literal['SLOT-001'] = 'SLOT-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Inspect prospective calendar schedule slots and verify availability.'
    return registry.apply(ToolRequest(slot_id=slot_id, request_id=request_id))

@mcp.tool()
def list_slots() -> list[dict]:
    """Query schedule slots allocated across the active calendar range."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
