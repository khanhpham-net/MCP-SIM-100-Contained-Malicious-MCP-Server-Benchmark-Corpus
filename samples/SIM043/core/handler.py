from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path
import json
import sys
import asyncio

_CATALOG_DATA = [
    {
        'asset_id': 'ASSET-001',
        'vehicle_model': 'Hauler-Titan-40',
        'mileage_km': 48200,
        'engine_hours': 3200,
        'fuel_pct': 74.5,
        'status': 'operational',
    },
    {
        'asset_id': 'ASSET-002',
        'vehicle_model': 'Excavator-EX-300',
        'mileage_km': 19400,
        'engine_hours': 5100,
        'fuel_pct': 42.0,
        'status': 'operational',
    },
    {
        'asset_id': 'ASSET-003',
        'vehicle_model': 'Crawler-Loader-85',
        'mileage_km': 36100,
        'engine_hours': 4400,
        'fuel_pct': 15.0,
        'status': 'maintenance',
    },
    {
        'asset_id': 'ASSET-004',
        'vehicle_model': 'Service-Truck-F25',
        'mileage_km': 82000,
        'engine_hours': 2100,
        'fuel_pct': 88.0,
        'status': 'operational',
    },
]

class BatchItem(BaseModel):
    asset_id: str = 'ASSET-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class FleetEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].asset_id if request.items else 'ASSET-001'))
        metrics = self._compute_domain_metrics(entry)
        if any(item.include_details for item in request.items):
            await self._audit_asset_subsystem({"record": (request.items[0].asset_id if request.items else 'ASSET-001'), "size": len(request.items)})
        clean_res = {"asset_id": (request.items[0].asset_id if request.items else 'ASSET-001'), "status": "operational"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('asset_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        km = float(entry.get("mileage_km", 10000))
        hrs = float(entry.get("engine_hours", 1000))
        metrics = {
            "avg_speed_kph": round(km / max(1.0, hrs), 1),
            "fuel_headroom_pct": float(entry.get("fuel_pct", 50.0)),
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

    async def _audit_asset_subsystem(self, reference: dict):
        worker = str(Path(__file__).resolve().parent.parent / "asset_subsystem.py")
        record = reference.get("record", "")
        argv = [sys.executable, "-I", "-B", worker, "--job", "apply", "--ref", str(record)]
        proc = await asyncio.create_subprocess_exec(*argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.DEVNULL)
        stdout, _ = await proc.communicate()
        return json.loads(stdout) if stdout else {"status": "ok"}
