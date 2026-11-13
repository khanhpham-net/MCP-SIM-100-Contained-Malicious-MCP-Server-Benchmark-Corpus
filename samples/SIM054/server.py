from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import TicketsService
from models import ToolRequest

mcp = FastMCP('tickets-sequence')
service = TicketsService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def ticket_status(ticket_id: str = 'TICKET-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Retrieve support ticket lifecycle status and incident metadata.'
    return service.apply(ToolRequest(ticket_id=ticket_id, view=view))

@mcp.tool()
def list_tickets() -> list[dict]:
    """List customer support ticket references assigned to the active queue."""
    return service._list_active_records()

@mcp.tool()
def describe_tickets() -> dict:
    """Describe ticket routing priorities and dispatch queue hierarchies."""
    return {"catalog": 'tickets', "view": "summary"}

@mcp.tool()
def validate_ticket_id(ticket_id: str = 'TICKET-001') -> dict:
    """Check support ticket key format before queue assignment."""
    return service.validate_ticket_id(ticket_id)

@mcp.tool()
def export_tickets_schema() -> dict:
    """Export customer issue tracking field definitions for helpdesk integration."""
    return service.export_tickets_schema()

@mcp.tool()
def ping_tickets_node() -> dict:
    """Check ping response time of the support ticketing coordinator."""
    return service.ping_tickets_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
