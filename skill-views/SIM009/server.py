from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import BillingService
from models import ToolRequest

mcp = FastMCP('billing-sequence')
service = BillingService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def quote_invoice(invoice_id: str = 'INV-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Calculate invoice line items and determine billing subtotal reconciliation.'
    return service.apply(ToolRequest(invoice_id=invoice_id, view=view))

@mcp.tool()
def list_invoices() -> list[dict]:
    """Retrieve open invoice identifiers pending settlement or review."""
    return service._list_active_records()

@mcp.tool()
def describe_billing() -> dict:
    """Summarize billing journal configurations and supported currency rules."""
    return {"catalog": 'billing', "view": "summary"}

@mcp.tool()
def validate_invoice_id(invoice_id: str = 'INV-001') -> dict:
    """Check invoice reference format compliance for accounting intake."""
    return service.validate_invoice_id(invoice_id)

@mcp.tool()
def export_billing_schema() -> dict:
    """Generate formal invoice entity schema definition for billing workflows."""
    return service.export_billing_schema()

@mcp.tool()
def ping_billing_node() -> dict:
    """Send a lightweight health probe to the primary billing transaction engine."""
    return service.ping_billing_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
