from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import TicketsEngine, BatchItem, ToolRequest

mcp = FastMCP('tickets-batch')
engine = TicketsEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def ticket_status(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Retrieve support ticket lifecycle status and incident metadata.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_tickets() -> list[dict]:
    """List customer support ticket references assigned to the active queue."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
