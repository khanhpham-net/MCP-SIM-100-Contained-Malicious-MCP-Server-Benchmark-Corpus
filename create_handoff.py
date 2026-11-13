"""Prepare scanner input records from reviewed admission metadata."""
from pathlib import Path
import json

from audit_corpus import ROOT, digest, write_json


def create(root=ROOT):
    manifest = json.loads((root / "benchmark-manifest.json").read_bytes())
    if digest((root / "evaluation/static-audit.json").read_bytes()) != manifest["static_audit_sha256"]:
        raise ValueError("Audit changed; regenerate benchmark manifest")
    target = root / "scan-results-template.json"
    if target.exists():
        previous = json.loads(target.read_bytes())
        if any(r.get("status") != "NOT_SCANNED" or r.get("prediction") is not None or r.get("raw_output")
               for r in previous.get("runs", [])):
            raise ValueError("Existing file contains results; preserve it before regenerating the template")
    lines = ["# Scanner Input Catalog / Danh mục input scanner", "",
             "> **English:** 100 source snapshots comprising 100 SIM samples. Admission is drawn from `benchmark-manifest.json`, not inferred from folder names.  ",
             "> **Tiếng Việt:** 100 source snapshot gồm 100 mẫu SIM. Admission lấy từ `benchmark-manifest.json`, không suy từ tên thư mục.", "",
             "| ID | Proposed Label / Nhãn đề xuất | Observed Mechanism / Cơ chế quan sát tĩnh | Admission | Source | Evidence |",
             "|---|---|---|---|---|---|"]
    routes = []
    for sample in manifest["samples"]:
        sid = sample["sample_id"]
        folder = f'{sample["source_directory"]}/{sid}'
        skill = root / "skill-views" / sid
        inputs = {
            "MCP Audit": (f"launch/{sid}.json", "config_or_live_metadata", "REQUIRES_CONFIG_RESOLUTION"),
            "MCTS": (folder, "repository_source", "AVAILABLE"),
            "Cisco MCP Scanner": (folder, "behavioral_source", "AVAILABLE"),
            "MCPShield": (f"launch/{sid}.json", "config_or_live_metadata", "REQUIRES_CONFIG_RESOLUTION"),
            "NVIDIA SkillSpector": (f"skill-views/{sid}" if skill.exists() else None, "derived_skill_directory", "AVAILABLE" if skill.exists() else "NOT_PREPARED"),
        }
        for scanner, (path, mode, input_status) in inputs.items():
            routes.append({"sample_id": sid, "scanner": scanner, "scanner_version": None,
                           "input": path, "mode_to_confirm": mode, "input_status": input_status,
                           "input_snapshot_sha256": sample["snapshot_sha256"],
                           "assessed_scope": None, "rubric_id": None, "model_or_analyzer": None,
                           "status": "NOT_SCANNED", "prediction": None, "findings": [],
                           "latency_seconds": None, "cost": None, "raw_output": None,
                           "raw_output_sha256": None, "scoring_eligible": sample["scoring_eligible"]})
        lines.append(f'| {sid} | {sample["proposed_malware_label"]} | {sample["observed_mechanism"]} | {sample["review_status"]} | [folder]({folder}/) | [static]({sample["static_evidence"]}) |')
    (root / "SAMPLE_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(target, {"note": "Copy selected rows to a results file. Missing skill views are NOT_PREPARED, not scanner UNSUPPORTED results.", "runs": routes})
    print(f"Prepared {len(routes)} NOT_SCANNED records for {len(manifest['samples'])} snapshots")


if __name__ == "__main__":
    create()
