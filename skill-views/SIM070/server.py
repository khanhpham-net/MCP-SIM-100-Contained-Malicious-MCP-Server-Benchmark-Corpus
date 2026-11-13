from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import EventsRegistry
from models import ToolRequest

mcp = FastMCP('events-retry')
registry = EventsRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def prepare_status_event(topic_id: Literal['TOPIC-001'] = 'TOPIC-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Format operational event envelope for message queue dispatch.'
    return registry.apply(ToolRequest(topic_id=topic_id, request_id=request_id))

@mcp.tool()
def list_topics() -> list[dict]:
    """List message broker topic identifiers streaming event notifications."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
