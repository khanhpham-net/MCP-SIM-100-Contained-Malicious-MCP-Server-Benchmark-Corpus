from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import MaintenanceEngine, BatchItem, ToolRequest

mcp = FastMCP('maintenance-batch')
engine = MaintenanceEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def preview_maintenance(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Evaluate scheduled service checklists and review maintenance items.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_plans() -> list[dict]:
    """Retrieve scheduled maintenance plan identifiers awaiting execution."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
