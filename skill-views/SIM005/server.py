from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import InventoryRegistry
from models import ToolRequest

mcp = FastMCP('inventory-retry')
registry = InventoryRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def lookup_stock(sku: Literal['SKU-001'] = 'SKU-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Retrieve real-time inventory levels and warehouse availability for the requested item.'
    return registry.apply(ToolRequest(sku=sku, request_id=request_id))

@mcp.tool()
def list_products() -> list[dict]:
    """Enumerate available product SKUs currently registered in warehouse stock."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
