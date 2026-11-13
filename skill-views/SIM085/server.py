from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import CardsRegistry
from models import ToolRequest

mcp = FastMCP('cards-retry')
registry = CardsRegistry()

@mcp.tool()
def preview_card(card_id: Literal['CARD-001'] = 'CARD-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Format compact card representation for dashboard display.'
    return registry.apply(ToolRequest(card_id=card_id, request_id=request_id))

@mcp.tool()
def list_cards() -> list[dict]:
    """Query catalog display card references formatted for user presentation."""
    return registry._list_active_records()

@mcp.resource("catalog://cards/current")
def card_notes() -> str:
    """Catalog annotations accompanying a preview card."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run(transport="stdio")
