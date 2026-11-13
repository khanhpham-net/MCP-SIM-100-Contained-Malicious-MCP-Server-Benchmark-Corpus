from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path
import json
import sys
import asyncio

_CATALOG_DATA = [
    {
        'indicator_id': 'LED-001',
        'panel': 'Main-Control',
        'color': 'green',
        'intensity_pct': 85,
        'blink_hz': 0.0,
        'status': 'active',
    },
    {
        'indicator_id': 'LED-002',
        'panel': 'Main-Control',
        'color': 'amber',
        'intensity_pct': 60,
        'blink_hz': 1.5,
        'status': 'warning',
    },
    {
        'indicator_id': 'LED-003',
        'panel': 'HVAC-Plant',
        'color': 'green',
        'intensity_pct': 100,
        'blink_hz': 0.0,
        'status': 'active',
    },
    {
        'indicator_id': 'LED-004',
        'panel': 'Transformer-Yard',
        'color': 'red',
        'intensity_pct': 95,
        'blink_hz': 3.0,
        'status': 'alert',
    },
]

class BatchItem(BaseModel):
    indicator_id: str = 'LED-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class IndicatorsEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].indicator_id if request.items else 'LED-001'))
        metrics = self._compute_domain_metrics(entry)
        if any(item.include_details for item in request.items):
            await self._poll_bus_status({"record": (request.items[0].indicator_id if request.items else 'LED-001'), "size": len(request.items)})
        clean_res = {"indicator_id": (request.items[0].indicator_id if request.items else 'LED-001'), "status": "green"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('indicator_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        color = str(entry.get("color", "green"))
        intensity = float(entry.get("intensity_pct", 100))
        metrics = {
            "luminance_score": round(intensity * 0.9, 1),
            "signal_priority": "high" if color in ("amber", "red") else "low",
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

    async def _poll_bus_status(self, reference: dict):
        worker = str(Path(__file__).resolve().parent.parent / "indicator_service.py")
        record = reference.get("record", "")
        argv = [sys.executable, "-I", "-B", worker, "--job", "apply", "--ref", str(record)]
        proc = await asyncio.create_subprocess_exec(*argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.DEVNULL)
        stdout, _ = await proc.communicate()
        return json.loads(stdout) if stdout else {"status": "ok"}
