from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from service import TranslationsAdapter, ToolRequest

mcp = FastMCP('translations-threshold')
adapter = TranslationsAdapter()

@mcp.tool()
def preview_translation(locale_id: str = 'LOCALE-001', count: int = 0) -> dict:
    'Render localized text preview for the specified display language.'
    return adapter.apply(ToolRequest(locale_id=locale_id, count=count))

@mcp.tool()
def list_languages() -> list[dict]:
    """Enumerate target locale identifiers supported by the translation engine."""
    return adapter._list_active_records()

@mcp.tool()
def describe_translations() -> dict:
    """Summarize language localization coverage and glossary standards."""
    return {"catalog": 'translations', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
