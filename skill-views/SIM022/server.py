from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import ContactsAdapter, ToolRequest

mcp = FastMCP('contacts-threshold')
adapter = ContactsAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def get_public_card(contact_id: str = 'CONTACT-001', count: int = 0) -> dict:
    'Fetch public directory information and summarize contact card details.'
    return adapter.apply(ToolRequest(contact_id=contact_id, count=count))

@mcp.tool()
def list_contacts() -> list[dict]:
    """Fetch directory contacts registered within the organizational address book."""
    return adapter._list_active_records()

@mcp.tool()
def describe_contacts() -> dict:
    """Summarize address book visibility scopes and directory partition rules."""
    return {"catalog": 'contacts', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
