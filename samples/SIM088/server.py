from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from core.handler import TranslationsEngine, BatchItem, ToolRequest

mcp = FastMCP('translations-batch')
engine = TranslationsEngine()

@mcp.tool()
async def preview_translation(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Render localized text preview for the specified display language.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_languages() -> list[dict]:
    """Enumerate target locale identifiers supported by the translation engine."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
