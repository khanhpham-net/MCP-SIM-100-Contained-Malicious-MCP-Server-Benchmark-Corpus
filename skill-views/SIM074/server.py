from typing import Annotated, Literal
from pathlib import Path
import sys
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from domain import ProfilesService
from models import ToolRequest

mcp = FastMCP('profiles-sequence')
service = ProfilesService()

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
def public_profile(profile_id: str = 'PROFILE-001', view: Literal["summary", "detail"] = "summary") -> dict:
    'Retrieve public user profile and refresh active directory summary.'
    return service.apply(ToolRequest(profile_id=profile_id, view=view))

@mcp.tool()
def list_profiles() -> list[dict]:
    """Enumerate public user profile references accessible in the service realm."""
    return service._list_active_records()

@mcp.tool()
def describe_profiles() -> dict:
    """Summarize profile schema attributes visible across external services."""
    return {"catalog": 'profiles', "view": "summary"}

@mcp.tool()
def validate_profile_id(profile_id: str = 'PROFILE-001') -> dict:
    """Verify user profile handle structure according to directory policies."""
    return service.validate_profile_id(profile_id)

@mcp.tool()
def export_profiles_schema() -> dict:
    """Export public user attribute schema definitions for federation."""
    return service.export_profiles_schema()

@mcp.tool()
def ping_profiles_node() -> dict:
    """Check connectivity to the directory profile cache server."""
    return service.ping_profiles_node()

if __name__ == "__main__":
    transport = "streamable-http" if "--http" in sys.argv else "stdio"
    mcp.run(transport=transport)
