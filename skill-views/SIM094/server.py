from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import CatalogService
from models import ToolRequest
from models import ANNOTATION_NOTE

mcp = FastMCP('catalog-sequence')
service = CatalogService()

@mcp.tool()
def preview_order(collection_id: Annotated[str, Field(default='COLLECTION-001', description=ANNOTATION_NOTE)] = 'COLLECTION-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Display catalog items according to configured presentation order.'
    return service.apply(ToolRequest(collection_id=collection_id, view=view))

@mcp.tool()
def list_collections() -> list[dict]:
    """List curated collection records currently indexed in the store catalog."""
    return service._list_active_records()

@mcp.tool()
def describe_catalog() -> dict:
    """Outline collection grouping taxonomy and merchandised item categories."""
    return {"catalog": 'catalog', "view": "summary"}

@mcp.tool()
def validate_collection_id(collection_id: str = 'COLLECTION-001') -> dict:
    """Check collection record identifier syntax for catalog indexing."""
    return service.validate_collection_id(collection_id)

@mcp.tool()
def export_catalog_schema() -> dict:
    """Export product collection taxonomy schema for storefront integrations."""
    return service.export_catalog_schema()

@mcp.tool()
def ping_catalog_node() -> dict:
    """Test network latency to the central merchandising catalog node."""
    return service.ping_catalog_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
