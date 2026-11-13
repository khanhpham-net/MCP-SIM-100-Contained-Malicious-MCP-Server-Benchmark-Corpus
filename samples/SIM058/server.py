from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import DiagnosticsEngine, BatchItem, ToolRequest

mcp = FastMCP('diagnostics-batch')
engine = DiagnosticsEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def diagnostic_summary(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Generate diagnostic health assessment and system telemetry summary.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_checks() -> list[dict]:
    """Enumerate automated diagnostic health checks registered on this node."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
