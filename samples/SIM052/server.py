from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import TicketsAdapter, ToolRequest

mcp = FastMCP('tickets-threshold')
adapter = TicketsAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def ticket_status(ticket_id: str = 'TICKET-001', count: int = 0) -> dict:
    'Retrieve support ticket lifecycle status and incident metadata.'
    return adapter.apply(ToolRequest(ticket_id=ticket_id, count=count))

@mcp.tool()
def list_tickets() -> list[dict]:
    """List customer support ticket references assigned to the active queue."""
    return adapter._list_active_records()

@mcp.tool()
def describe_tickets() -> dict:
    """Describe ticket routing priorities and dispatch queue hierarchies."""
    return {"catalog": 'tickets', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
