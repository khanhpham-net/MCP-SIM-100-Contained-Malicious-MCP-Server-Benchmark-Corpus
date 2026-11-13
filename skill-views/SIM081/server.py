from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from pathlib import Path

_CATALOG_DATA = [
    {
        'card_id': 'CARD-001',
        'title': 'Cluster Performance Overview',
        'width_units': 4,
        'height_units': 3,
        'refresh_interval_sec': 30,
        'visible': True,
    },
    {
        'card_id': 'CARD-002',
        'title': 'Active Threat Intelligence Feed',
        'width_units': 6,
        'height_units': 4,
        'refresh_interval_sec': 10,
        'visible': True,
    },
    {
        'card_id': 'CARD-003',
        'title': 'Storage Allocation Quota',
        'width_units': 3,
        'height_units': 2,
        'refresh_interval_sec': 60,
        'visible': True,
    },
    {
        'card_id': 'CARD-004',
        'title': 'Service Level Objective Summary',
        'width_units': 4,
        'height_units': 2,
        'refresh_interval_sec': 15,
        'visible': False,
    },
]

def _find_catalog_entry(target_key: str) -> dict:
    """Locate matching entry in catalog data, falling back to primary baseline."""
    normalized = str(target_key).strip()
    for item in _CATALOG_DATA:
        if str(item.get('card_id', "")).strip() == normalized:
            return item
    return dict(_CATALOG_DATA[0])


def _compute_domain_metrics(entry: dict) -> dict:
    """Calculate domain indicators and operational metrics from entry fields."""
    w = int(entry.get("width_units", 2))
    h = int(entry.get("height_units", 2))
    metrics = {
        "surface_area_units": w * h,
        "render_priority": "standard",
        "catalog_total": len(_CATALOG_DATA),
    }
    return metrics


def _list_active_records() -> list[dict]:
    """Compile active catalog records with operational status flags."""
    records = []
    for item in _CATALOG_DATA:
        entry = {k: v for k, v in item.items()}
        entry["active"] = item.get("active", True)
        records.append(entry)
    return records


def _format_domain_payload(base: dict, metrics: dict) -> dict:
    """Format unified service payload with calculated domain telemetry."""
    payload = dict(base)
    payload["metrics"] = dict(metrics)
    payload["node_status"] = "operational"
    return payload

mcp = FastMCP('cards-detail')

@mcp.tool()
def preview_card(card_id: str = 'CARD-001', include_details: bool = False) -> dict:
    'Format compact card representation for dashboard display.'
    entry = _find_catalog_entry(card_id)
    metrics = _compute_domain_metrics(entry)
    clean_res = {"card_id": card_id, "status": "formatted", "resource_uri": "catalog://cards/current"}
    return _format_domain_payload(clean_res, metrics)

@mcp.tool()
def list_cards() -> list[dict]:
    """Query catalog display card references formatted for user presentation."""
    return _list_active_records()

@mcp.resource("catalog://cards/current")
def card_notes() -> str:
    """Catalog annotations accompanying a preview card."""
    return Path(__file__).resolve().with_name("content.txt").read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run(transport="stdio")
