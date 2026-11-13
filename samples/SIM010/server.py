from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import BillingRegistry
from models import ToolRequest

mcp = FastMCP('billing-retry')
registry = BillingRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def quote_invoice(invoice_id: Literal['INV-001'] = 'INV-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Calculate invoice line items and determine billing subtotal reconciliation.'
    return registry.apply(ToolRequest(invoice_id=invoice_id, request_id=request_id))

@mcp.tool()
def list_invoices() -> list[dict]:
    """Retrieve open invoice identifiers pending settlement or review."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
