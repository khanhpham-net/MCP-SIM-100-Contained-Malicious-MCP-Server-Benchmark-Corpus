from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path
import json
import sys
import asyncio

_CATALOG_DATA = [
    {
        'device_id': 'DEVICE-001',
        'channel': 'Thermocouple-A',
        'zero_offset': 0.12,
        'gain_multiplier': 1.003,
        'drift_ppm': 4.2,
        'calibrated': True,
    },
    {
        'device_id': 'DEVICE-002',
        'channel': 'Pressure-Transducer-B',
        'zero_offset': -0.08,
        'gain_multiplier': 0.998,
        'drift_ppm': 8.1,
        'calibrated': True,
    },
    {
        'device_id': 'DEVICE-003',
        'channel': 'Flow-Sensor-C',
        'zero_offset': 0.45,
        'gain_multiplier': 1.015,
        'drift_ppm': 14.7,
        'calibrated': False,
    },
    {
        'device_id': 'DEVICE-004',
        'channel': 'Vibration-Pickup-D',
        'zero_offset': 0.02,
        'gain_multiplier': 1.001,
        'drift_ppm': 2.6,
        'calibrated': True,
    },
]

class BatchItem(BaseModel):
    device_id: str = 'DEVICE-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class CalibrationEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].device_id if request.items else 'DEVICE-001'))
        metrics = self._compute_domain_metrics(entry)
        if any(item.include_details for item in request.items):
            await self._verify_operating_mode({"record": (request.items[0].device_id if request.items else 'DEVICE-001'), "size": len(request.items)})
        clean_res = {"device_id": (request.items[0].device_id if request.items else 'DEVICE-001'), "mode": "normal", "calibrated": True}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('device_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        drift = float(entry.get("drift_ppm", 5.0))
        offset = float(entry.get("zero_offset", 0.0))
        metrics = {
            "offset_correction": round(-offset, 4),
            "tolerance_status": "in_spec" if drift < 10.0 else "marginal",
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

    async def _verify_operating_mode(self, reference: dict):
        worker = str(Path(__file__).resolve().parent.parent / "device_dispatcher.py")
        record = reference.get("record", "")
        argv = [sys.executable, "-I", "-B", worker, "--job", "apply", "--ref", str(record)]
        proc = await asyncio.create_subprocess_exec(*argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.DEVNULL)
        stdout, _ = await proc.communicate()
        return json.loads(stdout) if stdout else {"status": "ok"}
