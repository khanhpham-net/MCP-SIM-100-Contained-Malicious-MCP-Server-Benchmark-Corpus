from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import ContactsEngine, BatchItem, ToolRequest

mcp = FastMCP('contacts-batch')
engine = ContactsEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def get_public_card(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Fetch public directory information and summarize contact card details.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_contacts() -> list[dict]:
    """Fetch directory contacts registered within the organizational address book."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
