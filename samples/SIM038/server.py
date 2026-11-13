from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import CalibrationEngine, BatchItem, ToolRequest

mcp = FastMCP('calibration-batch')
engine = CalibrationEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def inspect_calibration(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Inspect system operating parameters and active calibration baseline.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_devices() -> list[dict]:
    """List hardware device profiles scheduled for calibration checks."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
