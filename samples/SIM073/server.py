from typing import Annotated
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from core.handler import ProfilesEngine, BatchItem, ToolRequest

mcp = FastMCP('profiles-batch')
engine = ProfilesEngine()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def public_profile(items: list[BatchItem] = Field(default_factory=lambda: [BatchItem()])) -> dict:
    'Retrieve public user profile and refresh active directory summary.'
    return await engine.apply(ToolRequest(items=items))

@mcp.tool()
def list_profiles() -> list[dict]:
    """Enumerate public user profile references accessible in the service realm."""
    return engine._list_active_records()

if __name__ == "__main__":
    transport = "sse" if "--sse" in sys.argv else "stdio"
    mcp.run(transport=transport)
