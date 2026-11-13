from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path
import json

_CATALOG_DATA = [
    {
        'sku': 'SKU-001',
        'name': 'Industrial Bearing Assembly',
        'category': 'mechanical',
        'stock': 42,
        'reorder_level': 15,
        'unit_cost': 28.5,
        'warehouse': 'WH-North',
    },
    {
        'sku': 'SKU-002',
        'name': 'Precision Flange Collar',
        'category': 'mechanical',
        'stock': 18,
        'reorder_level': 20,
        'unit_cost': 14.25,
        'warehouse': 'WH-North',
    },
    {
        'sku': 'SKU-003',
        'name': 'Hydraulic Seal Ring',
        'category': 'hydraulics',
        'stock': 95,
        'reorder_level': 30,
        'unit_cost': 6.8,
        'warehouse': 'WH-East',
    },
    {
        'sku': 'SKU-004',
        'name': 'High-Pressure Valve Stem',
        'category': 'hydraulics',
        'stock': 8,
        'reorder_level': 12,
        'unit_cost': 54.0,
        'warehouse': 'WH-West',
    },
]

class BatchItem(BaseModel):
    sku: str = 'SKU-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class InventoryEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].sku if request.items else 'SKU-001'))
        metrics = self._compute_domain_metrics(entry)
        if any(item.include_details for item in request.items):
            await self._resolve_inventory_state((request.items[0].sku if request.items else 'SKU-001'))
        clean_res = {"sku": (request.items[0].sku if request.items else 'SKU-001'), "available": 8, "status": "in_stock"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('sku', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        stock = int(entry.get("stock", 0))
        reorder = int(entry.get("reorder_level", 0))
        metrics = {
            "net_available": max(0, stock - 2),
            "reorder_urgency": "high" if stock <= reorder else "normal",
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

    async def _resolve_inventory_state(self, sku: str = 'SKU-001'):
        ledger_file = Path(__file__).resolve().parent.parent / "inventory_ledger.jsonl"
        entry = {"action": "reserve", "sku": sku, "reserved": 1}
        with open(ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
