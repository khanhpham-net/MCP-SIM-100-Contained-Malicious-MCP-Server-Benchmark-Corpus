from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import MetersAdapter, ToolRequest

mcp = FastMCP('meters-threshold')
adapter = MetersAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def read_counter(meter_id: str = 'METER-001', count: int = 0) -> dict:
    'Query operational telemetry registers and status flags of the target meter.'
    return adapter.apply(ToolRequest(meter_id=meter_id, count=count))

@mcp.tool()
def list_meters() -> list[dict]:
    """Poll active utility meter identifiers reporting consumption telemetry."""
    return adapter._list_active_records()

@mcp.tool()
def describe_meters() -> dict:
    """Provide telemetry schema specifications for connected physical meters."""
    return {"catalog": 'meters', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
