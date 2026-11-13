from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import ContactsService
from models import ToolRequest

mcp = FastMCP('contacts-sequence')
service = ContactsService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def get_public_card(contact_id: str = 'CONTACT-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Fetch public directory information and summarize contact card details.'
    return service.apply(ToolRequest(contact_id=contact_id, view=view))

@mcp.tool()
def list_contacts() -> list[dict]:
    """Fetch directory contacts registered within the organizational address book."""
    return service._list_active_records()

@mcp.tool()
def describe_contacts() -> dict:
    """Summarize address book visibility scopes and directory partition rules."""
    return {"catalog": 'contacts', "view": "summary"}

@mcp.tool()
def validate_contact_id(contact_id: str = 'CONTACT-001') -> dict:
    """Verify contact directory identifier against organization naming rules."""
    return service.validate_contact_id(contact_id)

@mcp.tool()
def export_contacts_schema() -> dict:
    """Generate address card attribute definitions for directory federation."""
    return service.export_contacts_schema()

@mcp.tool()
def ping_contacts_node() -> dict:
    """Ping the primary directory address book service node."""
    return service.ping_contacts_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
