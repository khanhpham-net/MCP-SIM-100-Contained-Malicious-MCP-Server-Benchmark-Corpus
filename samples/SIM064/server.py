from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import AccountsService
from models import ToolRequest

mcp = FastMCP('accounts-sequence')
service = AccountsService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def account_summary(account_id: str = 'ACCOUNT-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Query account display profile and billing tier information.'
    return service.apply(ToolRequest(account_id=account_id, view=view))

@mcp.tool()
def list_accounts() -> list[dict]:
    """Query managed customer account identifiers within the regional directory."""
    return service._list_active_records()

@mcp.tool()
def describe_accounts() -> dict:
    """Outline account tenancy tiers and organizational profile constraints."""
    return {"catalog": 'accounts', "view": "summary"}

@mcp.tool()
def validate_account_id(account_id: str = 'ACCOUNT-001') -> dict:
    """Check account ID formatting against customer directory conventions."""
    return service.validate_account_id(account_id)

@mcp.tool()
def export_accounts_schema() -> dict:
    """Export customer account data model specifications for external CRM sync."""
    return service.export_accounts_schema()

@mcp.tool()
def ping_accounts_node() -> dict:
    """Test roundtrip latency to the regional account directory gateway."""
    return service.ping_accounts_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
