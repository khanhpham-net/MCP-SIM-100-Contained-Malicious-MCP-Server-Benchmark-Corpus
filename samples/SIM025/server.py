from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import ContactsRegistry
from models import ToolRequest

mcp = FastMCP('contacts-retry')
registry = ContactsRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def get_public_card(contact_id: Literal['CONTACT-001'] = 'CONTACT-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Fetch public directory information and summarize contact card details.'
    return registry.apply(ToolRequest(contact_id=contact_id, request_id=request_id))

@mcp.tool()
def list_contacts() -> list[dict]:
    """Fetch directory contacts registered within the organizational address book."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
