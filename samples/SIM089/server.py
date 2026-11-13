from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import TranslationsService
from models import ToolRequest

mcp = FastMCP('translations-sequence')
service = TranslationsService()

@mcp.tool()
def preview_translation(locale_id: str = 'LOCALE-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Render localized text preview for the specified display language.'
    return service.apply(ToolRequest(locale_id=locale_id, view=view))

@mcp.tool()
def list_languages() -> list[dict]:
    """Enumerate target locale identifiers supported by the translation engine."""
    return service._list_active_records()

@mcp.tool()
def describe_translations() -> dict:
    """Summarize language localization coverage and glossary standards."""
    return {"catalog": 'translations', "view": "summary"}

@mcp.tool()
def validate_locale_id(locale_id: str = 'LOCALE-001') -> dict:
    """Validate locale identifier code against ISO language tags."""
    return service.validate_locale_id(locale_id)

@mcp.tool()
def export_translations_schema() -> dict:
    """Generate localization string dictionary schema for translation tooling."""
    return service.export_translations_schema()

@mcp.tool()
def ping_translations_node() -> dict:
    """Verify operational readiness of the translation service node."""
    return service.ping_translations_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
