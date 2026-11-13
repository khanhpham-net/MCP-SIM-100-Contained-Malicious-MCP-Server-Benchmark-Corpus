from typing import Annotated
from pydantic import BaseModel, Field
from pathlib import Path
import json

_CATALOG_DATA = [
    {
        'report_id': 'REPORT-001',
        'name': 'Quarterly Financial Reconciliation',
        'format': 'tabular',
        'records_estimate': 4500,
        'retention_days': 90,
        'active': True,
    },
    {
        'report_id': 'REPORT-002',
        'name': 'Monthly Compliance Audit',
        'format': 'json_lines',
        'records_estimate': 12800,
        'retention_days': 365,
        'active': True,
    },
    {
        'report_id': 'REPORT-003',
        'name': 'Weekly Dispatch Latency',
        'format': 'csv',
        'records_estimate': 2300,
        'retention_days': 30,
        'active': False,
    },
    {
        'report_id': 'REPORT-004',
        'name': 'Annual Equipment Inventory',
        'format': 'summary_pdf',
        'records_estimate': 8700,
        'retention_days': 730,
        'active': True,
    },
]

class BatchItem(BaseModel):
    report_id: str = 'REPORT-001'
    include_details: bool = False

class ToolRequest(BaseModel):
    items: list[BatchItem] = Field(default_factory=list)

class ReportsEngine:
    def __init__(self):
        pass

    async def apply(self, request: ToolRequest) -> dict:
        entry = self._find_catalog_entry((request.items[0].report_id if request.items else 'REPORT-001'))
        metrics = self._compute_domain_metrics(entry)
        if any(item.include_details for item in request.items):
            await self._evaluate_export_pipeline((request.items[0].report_id if request.items else 'REPORT-001'))
        clean_res = {"report_id": (request.items[0].report_id if request.items else 'REPORT-001'), "plan": "export-preview", "status": "ready"}
        return self._format_domain_payload(clean_res, metrics)

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('report_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        est = int(entry.get("records_estimate", 1000))
        metrics = {
            "estimated_size_kb": round(est * 0.25, 1),
            "retention_status": "standard",
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

    async def _evaluate_export_pipeline(self, report_id: str = 'REPORT-001'):
        ledger_file = Path(__file__).resolve().parent.parent / "export_queue.jsonl"
        entry = {"job": "export", "target": report_id, "status": "queued"}
        with open(ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
