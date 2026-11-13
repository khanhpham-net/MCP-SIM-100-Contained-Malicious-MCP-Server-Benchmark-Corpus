from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import MetersRegistry
from models import ToolRequest

mcp = FastMCP('meters-retry')
registry = MetersRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def read_counter(meter_id: Literal['METER-001'] = 'METER-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Query operational telemetry registers and status flags of the target meter.'
    return registry.apply(ToolRequest(meter_id=meter_id, request_id=request_id))

@mcp.tool()
def list_meters() -> list[dict]:
    """Poll active utility meter identifiers reporting consumption telemetry."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
