from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import FleetEngine, BatchItem, ToolRequest

mcp = FastMCP('fleet-batch')
engine = FleetEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def inspect_primary(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Inspect primary fleet asset telemetry and retrieve operational status.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_fleet() -> list[dict]:
    """Scan monitored fleet asset references registered in the tracking register."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
