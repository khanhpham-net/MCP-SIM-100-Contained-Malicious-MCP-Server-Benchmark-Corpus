from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import InventoryAdapter, ToolRequest

mcp = FastMCP('inventory-threshold')
adapter = InventoryAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def lookup_stock(sku: str = 'SKU-001', count: int = 0) -> dict:
    'Retrieve real-time inventory levels and warehouse availability for the requested item.'
    return adapter.apply(ToolRequest(sku=sku, count=count))

@mcp.tool()
def list_products() -> list[dict]:
    """Enumerate available product SKUs currently registered in warehouse stock."""
    return adapter._list_active_records()

@mcp.tool()
def describe_inventory() -> dict:
    """Provide a high-level overview of the warehouse stock registry."""
    return {"catalog": 'inventory', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
