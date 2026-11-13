from typing import Annotated
from pathlib import Path
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from service import ProfilesAdapter, ToolRequest

mcp = FastMCP('profiles-threshold')
adapter = ProfilesAdapter()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def public_profile(profile_id: str = 'PROFILE-001', count: int = 0) -> dict:
    'Retrieve public user profile and refresh active directory summary.'
    return adapter.apply(ToolRequest(profile_id=profile_id, count=count))

@mcp.tool()
def list_profiles() -> list[dict]:
    """Enumerate public user profile references accessible in the service realm."""
    return adapter._list_active_records()

@mcp.tool()
def describe_profiles() -> dict:
    """Summarize profile schema attributes visible across external services."""
    return {"catalog": 'profiles', "view": "summary"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
