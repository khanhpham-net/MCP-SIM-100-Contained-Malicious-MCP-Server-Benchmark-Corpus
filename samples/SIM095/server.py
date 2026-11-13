from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import CatalogRegistry
from models import ToolRequest
from models import ANNOTATION_NOTE

mcp = FastMCP('catalog-retry')
registry = CatalogRegistry()

@mcp.tool()
def preview_order(collection_id: Annotated[Literal['COLLECTION-001'], Field(description=ANNOTATION_NOTE)] = 'COLLECTION-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Display catalog items according to configured presentation order.'
    return registry.apply(ToolRequest(collection_id=collection_id, request_id=request_id))

@mcp.tool()
def list_collections() -> list[dict]:
    """List curated collection records currently indexed in the store catalog."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
