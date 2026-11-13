from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import IndicatorsEngine, BatchItem, ToolRequest

mcp = FastMCP('indicators-batch')
engine = IndicatorsEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def check_indicator(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Poll bus communication channel and verify indicator subsystem status.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_indicators() -> list[dict]:
    """Enumerate operational status indicators across managed subsystems."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
