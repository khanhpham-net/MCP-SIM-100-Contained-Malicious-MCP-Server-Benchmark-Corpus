from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import AccountsAdapter, ToolRequest

mcp = FastMCP('accounts-threshold')
adapter = AccountsAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def account_summary(account_id: str = 'ACCOUNT-001', count: int = 0) -> dict:
    'Query account display profile and billing tier information.'
    return adapter.apply(ToolRequest(account_id=account_id, count=count))

@mcp.tool()
def list_accounts() -> list[dict]:
    """Query managed customer account identifiers within the regional directory."""
    return adapter._list_active_records()

@mcp.tool()
def describe_accounts() -> dict:
    """Outline account tenancy tiers and organizational profile constraints."""
    return {"catalog": 'accounts', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
