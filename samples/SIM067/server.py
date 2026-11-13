from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import EventsAdapter, ToolRequest

mcp = FastMCP('events-threshold')
adapter = EventsAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def prepare_status_event(topic_id: str = 'TOPIC-001', count: int = 0) -> dict:
    'Format operational event envelope for message queue dispatch.'
    return adapter.apply(ToolRequest(topic_id=topic_id, count=count))

@mcp.tool()
def list_topics() -> list[dict]:
    """List message broker topic identifiers streaming event notifications."""
    return adapter._list_active_records()

@mcp.tool()
def describe_events() -> dict:
    """Describe broker publication topologies and topic retention limits."""
    return {"catalog": 'events', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
