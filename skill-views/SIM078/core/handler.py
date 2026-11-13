from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path

_CATALOG_DATA = [
    {
        'palette_id': 'PALETTE-001',
        'theme_name': 'Obsidian Slate',
        'primary_hex': '#1e293b',
        'accent_hex': '#0ea5e9',
        'contrast_ratio': 7.4,
        'mode': 'dark',
    },
    {
        'palette_id': 'PALETTE-002',
        'theme_name': 'Emerald Dawn',
        'primary_hex': '#064e3b',
        'accent_hex': '#10b981',
        'contrast_ratio': 6.8,
        'mode': 'dark',
    },
    {
        'palette_id': 'PALETTE-003',
        'theme_name': 'Nordic Frost',
        'primary_hex': '#f8fafc',
        'accent_hex': '#3b82f6',
        'contrast_ratio': 5.9,
        'mode': 'light',
    },
    {
        'palette_id': 'PALETTE-004',
        'theme_name': 'Crimson Sunset',
        'primary_hex': '#7f1d1d',
        'accent_hex': '#f43f5e',
        'contrast_ratio': 8.1,
        'mode': 'dark',
    },
]

class BatchItem(BaseModel):
    palette_id: str = 'PALETTE-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class PalettesEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].palette_id if request.items else 'PALETTE-001'))
        metrics = self._compute_domain_metrics(entry)
        clean_res = {"palette_id": (request.items[0].palette_id if request.items else 'PALETTE-001'), "status": "rendered"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('palette_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        contrast = float(entry.get("contrast_ratio", 5.0))
        metrics = {
            "wcag_aa_compliant": contrast >= 4.5,
            "wcag_aaa_compliant": contrast >= 7.0,
            "catalog_total": len(_CATALOG_DATA),
        }
        return metrics

    def _list_active_records(self) -> list[dict]:
        """Compile active catalog records with operational status flags."""
        records = []
        for item in _CATALOG_DATA:
            entry = {k: v for k, v in item.items()}
            entry["active"] = item.get("active", True)
            records.append(entry)
        return records

    def _format_domain_payload(self, base: dict, metrics: dict) -> dict:
        """Format unified service payload with calculated domain telemetry."""
        payload = dict(base)
        payload["metrics"] = dict(metrics)
        payload["node_status"] = "operational"
        return payload
