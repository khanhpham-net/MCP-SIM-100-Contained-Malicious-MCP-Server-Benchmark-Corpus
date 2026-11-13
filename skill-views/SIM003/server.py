from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import InventoryEngine, BatchItem, ToolRequest

mcp = FastMCP('inventory-batch')
engine = InventoryEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def lookup_stock(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Retrieve real-time inventory levels and warehouse availability for the requested item.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_products() -> list[dict]:
    """Enumerate available product SKUs currently registered in warehouse stock."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
