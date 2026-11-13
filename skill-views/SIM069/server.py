from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import EventsService
from models import ToolRequest

mcp = FastMCP('events-sequence')
service = EventsService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def prepare_status_event(topic_id: str = 'TOPIC-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Format operational event envelope for message queue dispatch.'
    return service.apply(ToolRequest(topic_id=topic_id, view=view))

@mcp.tool()
def list_topics() -> list[dict]:
    """List message broker topic identifiers streaming event notifications."""
    return service._list_active_records()

@mcp.tool()
def describe_events() -> dict:
    """Describe broker publication topologies and topic retention limits."""
    return {"catalog": 'events', "view": "summary"}

@mcp.tool()
def validate_topic_id(topic_id: str = 'TOPIC-001') -> dict:
    """Validate event topic naming syntax for message broker dispatch."""
    return service.validate_topic_id(topic_id)

@mcp.tool()
def export_events_schema() -> dict:
    """Output streaming event envelope schema for message bus subscribers."""
    return service.export_events_schema()

@mcp.tool()
def ping_events_node() -> dict:
    """Verify active broker node availability on the event message bus."""
    return service.ping_events_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
