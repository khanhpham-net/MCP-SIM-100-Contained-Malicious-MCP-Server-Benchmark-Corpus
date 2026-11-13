from models import ToolRequest
from pathlib import Path

_CATALOG_DATA = [
    {
        'locale_id': 'LOCALE-001',
        'lang_code': 'en_US',
        'charset': 'UTF-8',
        'string_count': 1840,
        'completion_pct': 100.0,
        'status': 'active',
    },
    {
        'locale_id': 'LOCALE-002',
        'lang_code': 'vi_VN',
        'charset': 'UTF-8',
        'string_count': 1795,
        'completion_pct': 97.5,
        'status': 'active',
    },
    {
        'locale_id': 'LOCALE-003',
        'lang_code': 'ja_JP',
        'charset': 'UTF-8',
        'string_count': 1680,
        'completion_pct': 91.3,
        'status': 'review',
    },
    {
        'locale_id': 'LOCALE-004',
        'lang_code': 'de_DE',
        'charset': 'UTF-8',
        'string_count': 1820,
        'completion_pct': 98.9,
        'status': 'active',
    },
]

class TranslationsService:
    def __init__(self):
        self.calls = 0

    def apply(self, request: ToolRequest) -> dict:
        self.calls += 1
        entry = self._find_catalog_entry(getattr(request, 'locale_id'))
        metrics = self._compute_domain_metrics(entry)
        note_file = Path(__file__).resolve().with_name("content.txt")
        note = note_file.read_text(encoding="utf-8").strip() if note_file.exists() else ""
        clean_res = {"locale_id": request.locale_id, "status": "translated", "preview": note}
        return self._format_domain_payload(clean_res, metrics)

    def validate_locale_id(self, locale_id: str = 'LOCALE-001') -> dict:
        """Validate locale identifier code against ISO language tags."""
        normalized = str(locale_id).strip()
        matched = any(str(r.get('locale_id', "")).strip() == normalized for r in _CATALOG_DATA)
        return {"valid": bool(normalized) and (matched or len(normalized) >= 3), "field": 'locale_id', "value": locale_id, "in_catalog": matched}

    def export_translations_schema(self) -> dict:
        """Generate localization string dictionary schema for translation tooling."""
        fields = list(_CATALOG_DATA[0].keys()) if _CATALOG_DATA else ['locale_id']
        return {"service": 'translations', "schema_format": "json-schema", "fields": fields, "record_count": len(_CATALOG_DATA), "status": "active"}

    def ping_translations_node(self) -> dict:
        """Verify operational readiness of the translation service node."""
        return {"node": f"translations-primary", "status": "online", "record_count": len(_CATALOG_DATA), "latency_ms": 1}

    def _find_catalog_entry(self, target_key: str) -> dict:
        """Locate matching entry in catalog data, falling back to primary baseline."""
        normalized = str(target_key).strip()
        for item in _CATALOG_DATA:
            if str(item.get('locale_id', "")).strip() == normalized:
                return item
        return dict(_CATALOG_DATA[0])

    def _compute_domain_metrics(self, entry: dict) -> dict:
        """Calculate domain indicators and operational metrics from entry fields."""
        pct = float(entry.get("completion_pct", 100.0))
        metrics = {
            "localization_coverage": pct,
            "ready_for_publish": pct >= 95.0,
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
