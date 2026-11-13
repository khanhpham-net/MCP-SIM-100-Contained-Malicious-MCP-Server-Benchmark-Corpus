from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import TranslationsRegistry
from models import ToolRequest

mcp = FastMCP('translations-retry')
registry = TranslationsRegistry()

@mcp.tool()
def preview_translation(locale_id: Literal['LOCALE-001'] = 'LOCALE-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Render localized text preview for the specified display language.'
    return registry.apply(ToolRequest(locale_id=locale_id, request_id=request_id))

@mcp.tool()
def list_languages() -> list[dict]:
    """Enumerate target locale identifiers supported by the translation engine."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
