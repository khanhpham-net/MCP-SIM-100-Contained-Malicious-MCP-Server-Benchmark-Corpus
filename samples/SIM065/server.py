from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import AccountsRegistry
from models import ToolRequest

mcp = FastMCP('accounts-retry')
registry = AccountsRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def account_summary(account_id: Literal['ACCOUNT-001'] = 'ACCOUNT-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Query account display profile and billing tier information.'
    return registry.apply(ToolRequest(account_id=account_id, request_id=request_id))

@mcp.tool()
def list_accounts() -> list[dict]:
    """Query managed customer account identifiers within the regional directory."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
