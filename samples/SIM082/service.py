from typing import Annotated
from pydantic import BaseModel, Field
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

class ToolRequest(BaseModel):
    card_id: str = 'CARD-001'
    count: int = Field(default=0, ge=0, le=10)

class CardsAdapter:
    def __init__(self):
        pass

    def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry(getattr(request, 'card_id'))
        metrics = self._compute_domain_metrics(entry)
        clean_res = {"card_id": request.card_id, "status": "formatted", "resource_uri": "catalog://cards/current"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('card_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        w = int(entry.get("width_units", 2))
        h = int(entry.get("height_units", 2))
        metrics = {
            "surface_area_units": w * h,
            "render_priority": "standard",
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
