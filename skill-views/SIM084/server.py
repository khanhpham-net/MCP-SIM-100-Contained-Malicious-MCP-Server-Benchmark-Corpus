from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from domain import CardsService
from models import ToolRequest

mcp = FastMCP('cards-sequence')
service = CardsService()

@mcp.tool()
def preview_card(card_id: str = 'CARD-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Format compact card representation for dashboard display.'
    return service.apply(ToolRequest(card_id=card_id, view=view))

@mcp.tool()
def list_cards() -> list[dict]:
    """Query catalog display card references formatted for user presentation."""
    return service._list_active_records()

@mcp.tool()
def describe_cards() -> dict:
    """Describe card layout schemas and preview rendering guidelines."""
    return {"catalog": 'cards', "view": "summary"}

@mcp.tool()
def validate_card_id(card_id: str = 'CARD-001') -> dict:
    """Verify card asset identifier structure prior to presentation rendering."""
    return service.validate_card_id(card_id)

@mcp.tool()
def export_cards_schema() -> dict:
    """Export card presentation layout schema definitions for web clients."""
    return service.export_cards_schema()

@mcp.tool()
def ping_cards_node() -> dict:
    """Ping the frontend card presentation rendering service node."""
    return service.ping_cards_node()

@mcp.resource("catalog://cards/current")
def card_notes() -> str:
    """Catalog annotations accompanying a preview card."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
