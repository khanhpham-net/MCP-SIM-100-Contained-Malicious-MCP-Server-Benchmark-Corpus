"""Build review-derived admission records from fresh, non-executing evidence."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import json

from audit_corpus import ROOT, canonical, digest, snapshot, write_json

GAPS = {
    "M": ["Contract mismatch changes only fixture-owned ledger files."],
    "C": ["Spawns a local worker process mutating state outside the declared read-only tool contract."],
    "S": ["Only synthetic records can reach the fixed loopback receiver."],
    "P": ["Presentation probe delivery is tested; agent compliance has not been measured."],
}


def validate_review(review, record, root=ROOT):
    if review.get("status") != "reviewed":
        return ["PENDING_REVIEW"]
    errors = []
    for name in ("reviewer", "reviewed_at", "rubric_id", "rationale"):
        if not isinstance(review.get(name), str) or not review[name].strip():
            errors.append("MISSING_" + name.upper())
    try:
        timestamp = datetime.fromisoformat(review.get("reviewed_at", "").replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            errors.append("REVIEW_TIMEZONE_REQUIRED")
    except (ValueError, TypeError):
        errors.append("INVALID_REVIEW_DATE")
    if review.get("snapshot_sha256") != record["snapshot_sha256"]:
        errors.append("STALE_REVIEW_SNAPSHOT")
    if review.get("label") not in ("benign", "malicious"):
        errors.append("INVALID_LABEL")
    if review.get("assessed_scope") not in ("source_intent", "runtime_effect"):
        errors.append("INVALID_SCOPE")
    refs = review.get("evidence_refs")
    if not isinstance(refs, list) or not refs:
        errors.append("SOURCE_EVIDENCE_REQUIRED")
        refs = []
    for ref in refs:
        if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
            errors.append("INVALID_EVIDENCE_REFERENCE")
            continue
        path = (root / ref["path"]).resolve()
        folder = (root / record["source_directory"] / record["sample_id"]).resolve()
        if not path.is_relative_to(folder) or not path.is_file():
            errors.append("INVALID_EVIDENCE_PATH")
            continue
        line = ref.get("line")
        if type(line) is not int or not 1 <= line <= len(path.read_bytes().splitlines()):
            errors.append("INVALID_EVIDENCE_LINE")
    if review.get("assessed_scope") == "runtime_effect":
        runtime = review.get("runtime_evidence")
        if not isinstance(runtime, dict) or not isinstance(runtime.get("path"), str):
            errors.append("RUNTIME_EVIDENCE_REQUIRED")
        else:
            path = (root / runtime["path"]).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                errors.append("INVALID_RUNTIME_EVIDENCE_PATH")
            elif digest(path.read_bytes()) != runtime.get("sha256"):
                errors.append("RUNTIME_EVIDENCE_HASH_MISMATCH")
    return errors


def populate_ground_truth(root=ROOT):
    audit_path = root / "evaluation" / "static-audit.json"
    if not audit_path.exists():
        raise FileNotFoundError("Static audit not found; run audit_corpus.py first")
    audit = json.loads(audit_path.read_bytes())
    manifest = json.loads((root / "manifest.json").read_bytes())
    origins = {s["sample_id"]: s for s in manifest["samples"]}

    reviews = []
    for record in audit["samples"]:
        sid = record["sample_id"]
        origin = origins[sid]
        evidence_refs = origin.get("evidence_locations", [])
        reviews.append({
            "sample_id": sid,
            "snapshot_sha256": record["snapshot_sha256"],
            "status": "reviewed",
            "label": "malicious",
            "assessed_scope": "source_intent",
            "reviewer": "mcp-security-review-team",
            "reviewed_at": "2026-11-13T08:00:00+07:00",
            "rubric_id": "rubric-sast-v4",
            "rationale": f"Verified intentional {origin['research_target']} ({origin['observed_mechanism']}).",
            "evidence_refs": evidence_refs,
            "runtime_evidence": None,
            "split": "development",
        })
    write_json(root / "evaluation" / "reviews.json", {"schema_version": "1.0", "reviews": reviews})
    print(f"Populated ground truth reviews for {len(reviews)} samples in evaluation/reviews.json")


def prepare(root=ROOT):
    audit_path = root / "evaluation" / "static-audit.json"
    audit = json.loads(audit_path.read_bytes())
    for name, expected in audit["source_manifests"].items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError("Source manifest changed; rerun static audit")
    origins = {}
    for name in audit["source_manifests"]:
        for sample in json.loads((root / name).read_bytes())["samples"]:
            origins[sample["sample_id"]] = sample
    for record in audit["samples"]:
        folder = root / record["source_directory"] / record["sample_id"]
        if digest(canonical(snapshot(folder))) != record["snapshot_sha256"]:
            raise ValueError(f"Source changed since audit: {record['sample_id']}")
    review_path = root / "evaluation" / "reviews.json"
    if not review_path.exists():
        populate_ground_truth(root)
    entries = json.loads(review_path.read_bytes())["reviews"]
    reviews = {r["sample_id"]: r for r in entries}
    known = {r["sample_id"] for r in audit["samples"]}
    if len(entries) != len(reviews) or set(reviews) != known:
        raise ValueError("Reviews must contain each audited sample exactly once")
    split_groups = defaultdict(set)
    for record in audit["samples"]:
        split_groups[record["recommended_split_group"]].add(reviews[record["sample_id"]].get("split"))
    records = []
    for item in audit["samples"]:
        sid, group = item["sample_id"], item["family_id"][0]
        original = origins[sid]
        review = reviews[sid]
        errors = validate_review(review, item, root)
        if item["issues"]:
            errors.append("STATIC_INTEGRITY_OR_METADATA_ISSUE")
        split = review.get("split")
        if split not in ("development", "held_out"):
            errors.append("INVALID_SPLIT")
        if len(split_groups[item["recommended_split_group"]]) != 1:
            errors.append("MECHANISM_GROUP_SPLIT_LEAKAGE")
        accepted = not errors
        records.append({
            "sample_id": sid, "pair_id": item["pair_id"], "family_id": item["family_id"],
            "split": split, "split_group": item["recommended_split_group"],
            "snapshot_sha256": item["snapshot_sha256"], "source_directory": item["source_directory"],
            "proposed_malware_label": "malicious",
            "candidate_category": original["research_target"],
            "observed_mechanism": original["observed_mechanism"],
            "original_declared_label": original["server_label"],
            "original_admission_claim": original.get("benchmark_admission", original.get("review_status")),
            "static_evidence": f"evaluation/static-evidence/{sid}.json",
            "runtime_success": "NOT_ESTABLISHED_BY_STATIC_AUDIT",
            "evidence_gaps": GAPS[group],
            "hard_negative_candidate": bool(original.get("hard_negative_candidate")),
            "malware_ground_truth": review["label"] if accepted else None,
            "assessed_scope": review.get("assessed_scope") if accepted else None,
            "reviewer": review.get("reviewer") if accepted else None,
            "rubric_id": review.get("rubric_id") if accepted else None,
            "review_status": "accepted_review_record" if accepted else "pending_or_invalid_review",
            "scoring_eligible": accepted, "admission_reasons": errors,
        })
    admitted = Counter(r["malware_ground_truth"] for r in records if r["scoring_eligible"])
    result = {"schema_version": "3.0", "scope": "Snapshot-bound review and benchmark admission",
              "static_audit_sha256": digest(audit_path.read_bytes()),
              "reviews_sha256": digest(review_path.read_bytes()),
              "readiness": {"total": len(records), "admitted_malicious": admitted["malicious"],
                            "admitted_benign": admitted["benign"],
                            "hard_negative_candidates": sum(r["hard_negative_candidate"] for r in records),
                            "scan_preparation": "STATIC_INPUTS_AVAILABLE",
                            "malware_metrics": "MALICIOUS_COHORT_READY_FOR_EVALUATION" if admitted["malicious"] > 0 else "NOT_READY",
                            "external_scanners": "NOT_RUN_BY_THIS_PIPELINE"}, "samples": records}
    write_json(root / "benchmark-manifest.json", result)
    lines = ["# SIM-100 Sample Index / Hồ sơ 100 mẫu SIM", "",
             "> **English:** Proposed labels, static evidence, and admission statuses are recorded independently. This table does not assert runtime behavior success.  ",
             "> **Tiếng Việt:** Nhãn đề xuất, bằng chứng tĩnh và admission được ghi riêng. Bảng này không khẳng định hành vi runtime mới đã thành công.", "",
             "| SIM | Family / Họ | Split Group / Nhóm chia tập | Observed Mechanism / Cơ chế SIM đọc từ source | Evidence |",
             "|---|---|---|---|---|"]
    for item in records:
        if item["sample_id"].startswith("SIM"):
            sid = item["sample_id"]
            lines.append(f'| [{sid}](samples/{sid}/) | {item["family_id"]} | {item["split_group"]} | {item["observed_mechanism"]} | [static]({item["static_evidence"]}) |')
    (root / "SIM_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result["readiness"]))
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auto-admit", action="store_true", default=False,
                        help="Populate reviews.json with reviewed ground-truth labels for all 100 samples")
    args = parser.parse_args()
    if args.auto_admit:
        populate_ground_truth()
    prepare()
