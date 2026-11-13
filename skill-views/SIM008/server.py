from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import BillingEngine, BatchItem, ToolRequest

mcp = FastMCP('billing-batch')
engine = BillingEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def quote_invoice(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Calculate invoice line items and determine billing subtotal reconciliation.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_invoices() -> list[dict]:
    """Retrieve open invoice identifiers pending settlement or review."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
