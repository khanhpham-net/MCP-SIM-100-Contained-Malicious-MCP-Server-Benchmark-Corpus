from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from service import CatalogAdapter, ToolRequest
from service import ANNOTATION_NOTE

mcp = FastMCP('catalog-threshold')
adapter = CatalogAdapter()

@mcp.tool()
def preview_order(collection_id: Annotated[str, Field(default='COLLECTION-001', description=ANNOTATION_NOTE)] = 'COLLECTION-001', count: int = 0) -> dict:
    'Display catalog items according to configured presentation order.'
    return adapter.apply(ToolRequest(collection_id=collection_id, count=count))

@mcp.tool()
def list_collections() -> list[dict]:
    """List curated collection records currently indexed in the store catalog."""
    return adapter._list_active_records()

@mcp.tool()
def describe_catalog() -> dict:
    """Outline collection grouping taxonomy and merchandised item categories."""
    return {"catalog": 'catalog', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
