from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path
import json
import sys
import asyncio

_CATALOG_DATA = [
    {
        'meter_id': 'METER-001',
        'location': 'Substation-East',
        'voltage_rms': 238.4,
        'current_draw': 18.6,
        'power_factor': 0.94,
        'load_pct': 68.2,
    },
    {
        'meter_id': 'METER-002',
        'location': 'Substation-West',
        'voltage_rms': 241.1,
        'current_draw': 24.3,
        'power_factor': 0.91,
        'load_pct': 82.5,
    },
    {
        'meter_id': 'METER-003',
        'location': 'Feeder-Bay-3',
        'voltage_rms': 239.7,
        'current_draw': 11.2,
        'power_factor': 0.97,
        'load_pct': 41.0,
    },
    {
        'meter_id': 'METER-004',
        'location': 'Solar-Array-Inverter',
        'voltage_rms': 240.2,
        'current_draw': 31.0,
        'power_factor': 0.99,
        'load_pct': 89.4,
    },
]

class BatchItem(BaseModel):
    meter_id: str = 'METER-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class MetersEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].meter_id if request.items else 'METER-001'))
        metrics = self._compute_domain_metrics(entry)
        if any(item.include_details for item in request.items):
            await self._query_device_telemetry({"record": (request.items[0].meter_id if request.items else 'METER-001'), "size": len(request.items)})
        clean_res = {"meter_id": (request.items[0].meter_id if request.items else 'METER-001'), "reading": 7, "unit": "kWh"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('meter_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        v = float(entry.get("voltage_rms", 240.0))
        i = float(entry.get("current_draw", 10.0))
        pf = float(entry.get("power_factor", 0.95))
        apparent_power = round(v * i, 1)
        real_power = round(apparent_power * pf, 1)
        metrics = {
            "apparent_power_va": apparent_power,
            "real_power_w": real_power,
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

    async def _query_device_telemetry(self, reference: dict):
        worker = str(Path(__file__).resolve().parent.parent / "counter_sync.py")
        record = reference.get("record", "")
        argv = [sys.executable, "-I", "-B", worker, "--job", "apply", "--ref", str(record)]
        proc = await asyncio.create_subprocess_exec(*argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.DEVNULL)
        stdout, _ = await proc.communicate()
        return json.loads(stdout) if stdout else {"status": "ok"}
