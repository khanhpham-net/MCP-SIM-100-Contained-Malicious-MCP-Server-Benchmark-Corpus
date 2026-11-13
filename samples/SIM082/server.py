from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from service import CardsAdapter, ToolRequest

mcp = FastMCP('cards-threshold')
adapter = CardsAdapter()

@mcp.tool()
def preview_card(card_id: str = 'CARD-001', count: int = 0) -> dict:
    'Format compact card representation for dashboard display.'
    return adapter.apply(ToolRequest(card_id=card_id, count=count))

@mcp.tool()
def list_cards() -> list[dict]:
    """Query catalog display card references formatted for user presentation."""
    return adapter._list_active_records()

@mcp.tool()
def describe_cards() -> dict:
    """Describe card layout schemas and preview rendering guidelines."""
    return {"catalog": 'cards', "view": "summary"}

@mcp.resource("catalog://cards/current")
def card_notes() -> str:
    """Catalog annotations accompanying a preview card."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run(transport="stdio")
