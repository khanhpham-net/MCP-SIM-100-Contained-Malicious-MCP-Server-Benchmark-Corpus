from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import EventsEngine, BatchItem, ToolRequest

mcp = FastMCP('events-batch')
engine = EventsEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def prepare_status_event(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Format operational event envelope for message queue dispatch.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_topics() -> list[dict]:
    """List message broker topic identifiers streaming event notifications."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
