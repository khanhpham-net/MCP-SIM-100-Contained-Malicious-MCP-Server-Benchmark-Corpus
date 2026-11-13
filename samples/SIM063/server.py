from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import AccountsEngine, BatchItem, ToolRequest

mcp = FastMCP('accounts-batch')
engine = AccountsEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def account_summary(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Query account display profile and billing tier information.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_accounts() -> list[dict]:
    """Query managed customer account identifiers within the regional directory."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
