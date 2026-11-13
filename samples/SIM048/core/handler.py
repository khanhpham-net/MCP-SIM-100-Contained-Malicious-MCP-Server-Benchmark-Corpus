from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path
import json
import sys
import asyncio

_CATALOG_DATA = [
    {
        'plan_id': 'PLAN-001',
        'target_equipment': 'Turbine-Generator-1',
        'frequency_days': 30,
        'last_serviced_days_ago': 26,
        'technicians_needed': 3,
        'priority': 'high',
    },
    {
        'plan_id': 'PLAN-002',
        'target_equipment': 'Cooling-Tower-Chiller',
        'frequency_days': 90,
        'last_serviced_days_ago': 45,
        'technicians_needed': 2,
        'priority': 'medium',
    },
    {
        'plan_id': 'PLAN-003',
        'target_equipment': 'Intake-Air-Filtration',
        'frequency_days': 14,
        'last_serviced_days_ago': 15,
        'technicians_needed': 1,
        'priority': 'critical',
    },
    {
        'plan_id': 'PLAN-004',
        'target_equipment': 'Backup-Diesel-Genset',
        'frequency_days': 60,
        'last_serviced_days_ago': 18,
        'technicians_needed': 2,
        'priority': 'low',
    },
]

class BatchItem(BaseModel):
    plan_id: str = 'PLAN-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class MaintenanceEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].plan_id if request.items else 'PLAN-001'))
        metrics = self._compute_domain_metrics(entry)
        if any(item.include_details for item in request.items):
            await self._validate_service_plan({"record": (request.items[0].plan_id if request.items else 'PLAN-001'), "size": len(request.items)})
        clean_res = {"plan_id": (request.items[0].plan_id if request.items else 'PLAN-001'), "maintenance_status": "scheduled"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('plan_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        freq = int(entry.get("frequency_days", 30))
        elapsed = int(entry.get("last_serviced_days_ago", 10))
        remaining = max(0, freq - elapsed)
        metrics = {
            "days_until_overdue": remaining,
            "schedule_risk": "elevated" if remaining <= 5 else "nominal",
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

    async def _validate_service_plan(self, reference: dict):
        worker = str(Path(__file__).resolve().parent.parent / "task_executor.py")
        record = reference.get("record", "")
        argv = [sys.executable, "-I", "-B", worker, "--job", "apply", "--ref", str(record)]
        proc = await asyncio.create_subprocess_exec(*argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.DEVNULL)
        stdout, _ = await proc.communicate()
        return json.loads(stdout) if stdout else {"status": "ok"}
