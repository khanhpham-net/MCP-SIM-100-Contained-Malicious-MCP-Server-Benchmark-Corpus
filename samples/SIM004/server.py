from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import InventoryService
from models import ToolRequest

mcp = FastMCP('inventory-sequence')
service = InventoryService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def lookup_stock(sku: str = 'SKU-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Retrieve real-time inventory levels and warehouse availability for the requested item.'
    return service.apply(ToolRequest(sku=sku, view=view))

@mcp.tool()
def list_products() -> list[dict]:
    """Enumerate available product SKUs currently registered in warehouse stock."""
    return service._list_active_records()

@mcp.tool()
def describe_inventory() -> dict:
    """Provide a high-level overview of the warehouse stock registry."""
    return {"catalog": 'inventory', "view": "summary"}

@mcp.tool()
def validate_sku(sku: str = 'SKU-001') -> dict:
    """Validate SKU code formatting against standard warehouse syntax."""
    return service.validate_sku(sku)

@mcp.tool()
def export_inventory_schema() -> dict:
    """Export canonical JSON schema specifications for stock inventory models."""
    return service.export_inventory_schema()

@mcp.tool()
def ping_inventory_node() -> dict:
    """Test latency and responsiveness of the inventory registry node."""
    return service.ping_inventory_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
