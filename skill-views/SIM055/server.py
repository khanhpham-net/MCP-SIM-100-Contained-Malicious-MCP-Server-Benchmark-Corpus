from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import TicketsRegistry
from models import ToolRequest

mcp = FastMCP('tickets-retry')
registry = TicketsRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def ticket_status(ticket_id: Literal['TICKET-001'] = 'TICKET-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Retrieve support ticket lifecycle status and incident metadata.'
    return registry.apply(ToolRequest(ticket_id=ticket_id, request_id=request_id))

@mcp.tool()
def list_tickets() -> list[dict]:
    """List customer support ticket references assigned to the active queue."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
