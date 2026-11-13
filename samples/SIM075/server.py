from typing import Annotated, Literal
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import ProfilesRegistry
from models import ToolRequest

mcp = FastMCP('profiles-retry')
registry = ProfilesRegistry()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def public_profile(profile_id: Literal['PROFILE-001'] = 'PROFILE-001', request_id: Annotated[str, Field(min_length=1, max_length=64)] = "first-request") -> dict:
    'Retrieve public user profile and refresh active directory summary.'
    return registry.apply(ToolRequest(profile_id=profile_id, request_id=request_id))

@mcp.tool()
def list_profiles() -> list[dict]:
    """Enumerate public user profile references accessible in the service realm."""
    return registry._list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
