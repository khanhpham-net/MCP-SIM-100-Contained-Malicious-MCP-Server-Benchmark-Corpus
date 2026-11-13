"""Score normalized results against reviewed labels, reporting incomplete coverage."""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import json

from audit_corpus import ROOT, canonical, digest, snapshot, write_json

STATUSES = {"COMPLETED", "ERROR", "TIMEOUT", "PARTIAL", "UNSUPPORTED", "NOT_SCANNED"}


def score(manifest, results):
    required = ("scanner", "scanner_version", "mode", "assessed_scope", "rubric_id")
    if any(not isinstance(results.get(k), str) or not results[k].strip() for k in required):
        raise ValueError("Scanner, version, mode, scope and rubric_id are required")
    labels = {r["sample_id"]: r for r in manifest["samples"]}
    rows = results.get("runs", [])
    runs = {r["sample_id"]: r for r in rows}
    if len(runs) != len(rows) or not set(runs).issubset(labels):
        raise ValueError("Duplicate or unknown sample IDs")
    status_counts, excluded, confusion = Counter(), Counter(), Counter(TP=0, FP=0, TN=0, FN=0)
    scored = []
    eligible = 0
    for sid, record in labels.items():
        run = runs.get(sid, {"status": "NOT_SCANNED"})
        status = run.get("status")
        if status not in STATUSES:
            raise ValueError(f"Invalid status: {sid}")
        status_counts[status] += 1
        if not record["scoring_eligible"]:
            excluded["label_not_admitted"] += 1
            continue
        if record["assessed_scope"] != results["assessed_scope"] or record["rubric_id"] != results["rubric_id"]:
            excluded["scope_or_rubric_mismatch"] += 1
            continue
        eligible += 1
        if status != "COMPLETED":
            excluded[status] += 1
            continue
        if run.get("input_snapshot_sha256") != record["snapshot_sha256"]:
            excluded["snapshot_mismatch"] += 1
            continue
        prediction = run.get("prediction")
        if prediction not in ("benign", "malicious") or not run.get("raw_output"):
            excluded["invalid_prediction_or_missing_raw_output"] += 1
            continue
        truth = record["malware_ground_truth"]
        if truth not in ("benign", "malicious"):
            raise ValueError("Admitted sample lacks a valid ground-truth label")
        key = ("T" if prediction == truth else "F") + ("P" if prediction == "malicious" else "N")
        confusion[key] += 1
        scored.append(sid)
    tp, fp, tn, fn = (confusion[k] for k in ("TP", "FP", "TN", "FN"))
    metrics = None
    if tp + fn and tn + fp:
        metrics = {
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn), "fpr": fp / (fp + tn),
            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        }

    single_class_recall = tp / (tp + fn) if (tp + fn) else None

    group_confusion = defaultdict(Counter)
    edge_confusion = defaultdict(Counter)
    for sid in scored:
        record = labels[sid]
        run = runs[sid]
        grp = record.get("family_id", sid)[0]
        edg = record.get("edge_id")
        if not edg:
            edg = f"E{((int(sid[3:]) - 1) % 5) + 1}" if sid.startswith("SIM") else "E1"
        prediction = run.get("prediction")
        truth = record["malware_ground_truth"]
        key = ("T" if prediction == truth else "F") + ("P" if prediction == "malicious" else "N")
        group_confusion[grp][key] += 1
        edge_confusion[edg][key] += 1

    group_recall = {
        grp: group_confusion[grp]["TP"] / (group_confusion[grp]["TP"] + group_confusion[grp]["FN"])
        if (group_confusion[grp]["TP"] + group_confusion[grp]["FN"]) > 0 else None
        for grp in sorted(group_confusion)
    }
    edge_recall = {
        edg: edge_confusion[edg]["TP"] / (edge_confusion[edg]["TP"] + edge_confusion[edg]["FN"])
        if (edge_confusion[edg]["TP"] + edge_confusion[edg]["FN"]) > 0 else None
        for edg in sorted(edge_confusion)
    }

    return {"scanner": results["scanner"], "scanner_version": results["scanner_version"],
            "mode": results["mode"], "assessed_scope": results["assessed_scope"], "rubric_id": results["rubric_id"],
            "manifest_samples": len(labels), "eligible_for_this_scope": eligible,
            "scored_samples": len(scored), "scored_sample_ids": scored,
            "status_counts": dict(status_counts), "exclusion_counts": dict(excluded),
            "coverage": len(scored) / eligible if eligible else None,
            "confusion_matrix": dict(confusion), "metrics": metrics,
            "single_class_recall": single_class_recall,
            "group_recall": group_recall,
            "edge_recall": edge_recall,
            "metric_scope": "completed_snapshot_matching_admitted_samples_only",
            "note": "Both reviewed classes must occur in the scored subset. Missing/error/partial runs remain excluded with reported coverage."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "benchmark-manifest.json").read_bytes())
    for filename, field in [("evaluation/static-audit.json", "static_audit_sha256"), ("evaluation/reviews.json", "reviews_sha256")]:
        if digest((ROOT / filename).read_bytes()) != manifest[field]:
            raise ValueError("Review/audit changed; regenerate benchmark manifest")
    for record in manifest["samples"]:
        folder = ROOT / record["source_directory"] / record["sample_id"]
        if digest(canonical(snapshot(folder))) != record["snapshot_sha256"]:
            raise ValueError("Source changed; regenerate audit and review changed snapshots")
    results = json.loads(args.results.read_bytes())
    for row in results.get("runs", []):
        raw = row.get("raw_output")
        if row.get("status") == "COMPLETED" and raw:
            path = (ROOT / raw).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                raise ValueError("Raw output file must exist inside the corpus workspace")
            if digest(path.read_bytes()) != row.get("raw_output_sha256"):
                raise ValueError("Raw output hash mismatch")
    report = score(manifest, results)
    write_json(args.output, report)
    print(json.dumps({"scored_samples": report["scored_samples"], "metrics": report["metrics"], "single_class_recall": report["single_class_recall"]}))


if __name__ == "__main__":
    main()
