from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from pathlib import Path

_CATALOG_DATA = [
    {
        'locale_id': 'LOCALE-001',
        'lang_code': 'en_US',
        'charset': 'UTF-8',
        'string_count': 1840,
        'completion_pct': 100.0,
        'status': 'active',
    },
    {
        'locale_id': 'LOCALE-002',
        'lang_code': 'vi_VN',
        'charset': 'UTF-8',
        'string_count': 1795,
        'completion_pct': 97.5,
        'status': 'active',
    },
    {
        'locale_id': 'LOCALE-003',
        'lang_code': 'ja_JP',
        'charset': 'UTF-8',
        'string_count': 1680,
        'completion_pct': 91.3,
        'status': 'review',
    },
    {
        'locale_id': 'LOCALE-004',
        'lang_code': 'de_DE',
        'charset': 'UTF-8',
        'string_count': 1820,
        'completion_pct': 98.9,
        'status': 'active',
    },
]

def _find_catalog_entry(target_key: str) -> dict:
    """Locate matching entry in catalog data, falling back to primary baseline."""
    normalized = str(target_key).strip()
    for item in _CATALOG_DATA:
        if str(item.get('locale_id', "")).strip() == normalized:
            return item
    return dict(_CATALOG_DATA[0])


def _compute_domain_metrics(entry: dict) -> dict:
    """Calculate domain indicators and operational metrics from entry fields."""
    pct = float(entry.get("completion_pct", 100.0))
    metrics = {
        "localization_coverage": pct,
        "ready_for_publish": pct >= 95.0,
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

mcp = FastMCP('translations-detail')

@mcp.tool()
def preview_translation(locale_id: str = 'LOCALE-001', include_details: bool = False) -> dict:
    'Render localized text preview for the specified display language.'
    entry = _find_catalog_entry(locale_id)
    metrics = _compute_domain_metrics(entry)
    note_file = Path(__file__).resolve().with_name("content.txt")
    note = note_file.read_text(encoding="utf-8").strip() if note_file.exists() else ""
    clean_res = {"locale_id": locale_id, "status": "translated", "preview": note}
    return _format_domain_payload(clean_res, metrics)

@mcp.tool()
def list_languages() -> list[dict]:
    """Enumerate target locale identifiers supported by the translation engine."""
    return _list_active_records()

if __name__ == "__main__":
    mcp.run(transport="stdio")
