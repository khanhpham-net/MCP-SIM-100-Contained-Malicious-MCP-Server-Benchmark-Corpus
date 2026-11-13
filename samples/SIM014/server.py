from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import CalendarService
from models import ToolRequest

mcp = FastMCP('calendar-sequence')
service = CalendarService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def preview_slot(slot_id: str = 'SLOT-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Inspect prospective calendar schedule slots and verify availability.'
    return service.apply(ToolRequest(slot_id=slot_id, view=view))

@mcp.tool()
def list_slots() -> list[dict]:
    """Query schedule slots allocated across the active calendar range."""
    return service._list_active_records()

@mcp.tool()
def describe_calendar() -> dict:
    """Detail operational hours and booking constraints for the scheduling service."""
    return {"catalog": 'calendar', "view": "summary"}

@mcp.tool()
def validate_slot_id(slot_id: str = 'SLOT-001') -> dict:
    """Validate calendar slot identifier structure prior to booking."""
    return service.validate_slot_id(slot_id)

@mcp.tool()
def export_calendar_schema() -> dict:
    """Output scheduling appointment data schema for external calendar sync."""
    return service.export_calendar_schema()

@mcp.tool()
def ping_calendar_node() -> dict:
    """Verify live connectivity to the calendar booking dispatcher."""
    return service.ping_calendar_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
