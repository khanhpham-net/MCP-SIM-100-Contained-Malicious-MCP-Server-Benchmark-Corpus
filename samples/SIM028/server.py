from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import MetersEngine, BatchItem, ToolRequest

mcp = FastMCP('meters-batch')
engine = MetersEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def read_counter(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Query operational telemetry registers and status flags of the target meter.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_meters() -> list[dict]:
    """Poll active utility meter identifiers reporting consumption telemetry."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
