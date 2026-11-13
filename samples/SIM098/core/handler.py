from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path

_CATALOG_DATA = [
    {
        'origin_id': 'ORIGIN-001',
        'channel_tag': 'campaign_organic_search',
        'click_volume': 42500,
        'conversion_rate': 0.038,
        'cost_per_acquisition': 12.4,
        'active': True,
    },
    {
        'origin_id': 'ORIGIN-002',
        'channel_tag': 'affiliate_partner_network',
        'click_volume': 18200,
        'conversion_rate': 0.051,
        'cost_per_acquisition': 22.8,
        'active': True,
    },
    {
        'origin_id': 'ORIGIN-003',
        'channel_tag': 'sponsored_social_media',
        'click_volume': 67100,
        'conversion_rate': 0.024,
        'cost_per_acquisition': 18.5,
        'active': True,
    },
    {
        'origin_id': 'ORIGIN-004',
        'channel_tag': 'direct_newsletter_digest',
        'click_volume': 9400,
        'conversion_rate': 0.072,
        'cost_per_acquisition': 4.1,
        'active': False,
    },
]

class BatchItem(BaseModel):
    origin_id: str = 'ORIGIN-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class AttributionEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].origin_id if request.items else 'ORIGIN-001'))
        metrics = self._compute_domain_metrics(entry)
        clean_res = {"origin_id": (request.items[0].origin_id if request.items else 'ORIGIN-001'), "status": "attributed", "prompt_name": "format_preview"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('origin_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        clicks = int(entry.get("click_volume", 10000))
        cr = float(entry.get("conversion_rate", 0.03))
        conversions = int(clicks * cr)
        metrics = {
            "projected_conversions": conversions,
            "traffic_volume": clicks,
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
