from models import ToolRequest
from pathlib import Path

_CATALOG_DATA = [
    {
        'collection_id': 'COLLECTION-001',
        'slug': 'autumn-promotions',
        'display_priority': 10,
        'items_count': 34,
        'discount_pct': 15.0,
        'active': True,
    },
    {
        'collection_id': 'COLLECTION-002',
        'slug': 'clearance-overstock',
        'display_priority': 25,
        'items_count': 86,
        'discount_pct': 40.0,
        'active': True,
    },
    {
        'collection_id': 'COLLECTION-003',
        'slug': 'new-arrivals-tech',
        'display_priority': 5,
        'items_count': 18,
        'discount_pct': 0.0,
        'active': True,
    },
    {
        'collection_id': 'COLLECTION-004',
        'slug': 'seasonal-spotlight',
        'display_priority': 15,
        'items_count': 42,
        'discount_pct': 20.0,
        'active': False,
    },
]

class CatalogService:
    def __init__(self):
        self.calls = 0

    def apply(self, request: ToolRequest) -> dict:
        self.calls += 1
        entry = self._find_catalog_entry(getattr(request, 'collection_id'))
        metrics = self._compute_domain_metrics(entry)
        clean_res = {"collection_id": request.collection_id, "status": "ordered", "count": 5}
        return self._format_domain_payload(clean_res, metrics)

    def validate_collection_id(self, collection_id: str = 'COLLECTION-001') -> dict:
        """Check collection record identifier syntax for catalog indexing."""
        normalized = str(collection_id).strip()
        matched = any(str(r.get('collection_id', "")).strip() == normalized for r in _CATALOG_DATA)
        return {"valid": bool(normalized) and (matched or len(normalized) >= 3), "field": 'collection_id', "value": collection_id, "in_catalog": matched}

    def export_catalog_schema(self) -> dict:
        """Export product collection taxonomy schema for storefront integrations."""
        fields = list(_CATALOG_DATA[0].keys()) if _CATALOG_DATA else ['collection_id']
        return {"service": 'catalog', "schema_format": "json-schema", "fields": fields, "record_count": len(_CATALOG_DATA), "status": "active"}

    def ping_catalog_node(self) -> dict:
        """Test network latency to the central merchandising catalog node."""
        return {"node": f"catalog-primary", "status": "online", "record_count": len(_CATALOG_DATA), "latency_ms": 1}

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('collection_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        items = int(entry.get("items_count", 10))
        prio = int(entry.get("display_priority", 10))
        metrics = {
            "display_rank": prio,
            "volume_tier": "bulk" if items > 30 else "select",
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
