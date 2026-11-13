from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import BillingAdapter, ToolRequest

mcp = FastMCP('billing-threshold')
adapter = BillingAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def quote_invoice(invoice_id: str = 'INV-001', count: int = 0) -> dict:
    'Calculate invoice line items and determine billing subtotal reconciliation.'
    return adapter.apply(ToolRequest(invoice_id=invoice_id, count=count))

@mcp.tool()
def list_invoices() -> list[dict]:
    """Retrieve open invoice identifiers pending settlement or review."""
    return adapter._list_active_records()

@mcp.tool()
def describe_billing() -> dict:
    """Summarize billing journal configurations and supported currency rules."""
    return {"catalog": 'billing', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
