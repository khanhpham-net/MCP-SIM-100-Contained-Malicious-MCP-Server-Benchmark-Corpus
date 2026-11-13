from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from core.handler import CardsEngine, BatchItem, ToolRequest

mcp = FastMCP('cards-batch')
engine = CardsEngine()

@mcp.tool()
async def preview_card(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Format compact card representation for dashboard display.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_cards() -> list[dict]:
    """Query catalog display card references formatted for user presentation."""
    return engine._list_active_records()

@mcp.resource("catalog://cards/current")
def card_notes() -> str:
    """Catalog annotations accompanying a preview card."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
