"""Regression checks for admission/scoring; executes no corpus sample."""
from pathlib import Path
import copy
import tempfile
import unittest

from audit_corpus import assign_groups
from prepare_evaluation import validate_review
from score_results import score


class EvaluationTests(unittest.TestCase):
    def record(self, sid, truth):
        return {"sample_id": sid, "scoring_eligible": True, "assessed_scope": "source_intent",
                "rubric_id": "rubric-test", "snapshot_sha256": sid + "-hash", "malware_ground_truth": truth}

    def result(self, rows):
        return {"scanner": "test", "scanner_version": "1", "mode": "source_tree",
                "assessed_scope": "source_intent", "rubric_id": "rubric-test", "runs": rows}

    def row(self, sid, prediction, status="COMPLETED"):
        return {"sample_id": sid, "status": status, "prediction": prediction,
                "input_snapshot_sha256": sid + "-hash", "raw_output": "test-only-placeholder.json"}

    def test_confusion_matrix(self):
        manifest = {"samples": [self.record("a", "malicious"), self.record("b", "malicious"), self.record("c", "benign"), self.record("d", "benign")]}
        report = score(manifest, self.result([self.row("a", "malicious"), self.row("b", "benign"), self.row("c", "malicious"), self.row("d", "benign")]))
        self.assertEqual(report["confusion_matrix"], {"TP": 1, "FP": 1, "TN": 1, "FN": 1})
        self.assertEqual(report["metrics"], {"precision": .5, "recall": .5, "fpr": .5, "f1": .5})

    def test_failed_missing_or_partial_never_become_safe(self):
        manifest = {"samples": [self.record(sid, "malicious") for sid in "abc"]}
        report = score(manifest, self.result([self.row("a", "benign", "ERROR"), self.row("b", "benign", "PARTIAL")]))
        self.assertEqual(report["scored_samples"], 0)
        self.assertEqual(report["status_counts"], {"ERROR": 1, "PARTIAL": 1, "NOT_SCANNED": 1})
        self.assertIsNone(report["metrics"])

    def test_single_class_does_not_yield_benchmark_metrics(self):
        report = score({"samples": [self.record("a", "malicious")]}, self.result([self.row("a", "malicious")]))
        self.assertIsNone(report["metrics"])

    def test_pending_scope_and_hash_excluded(self):
        records = [self.record(s, "benign") for s in "abc"]
        records[0]["scoring_eligible"] = False
        records[1]["assessed_scope"] = "runtime_effect"
        rows = [self.row(s, "malicious") for s in "abc"]
        rows[2]["input_snapshot_sha256"] = "changed"
        report = score({"samples": records}, self.result(rows))
        self.assertEqual(report["scored_samples"], 0)
        self.assertEqual(set(report["exclusion_counts"]), {"label_not_admitted", "scope_or_rubric_mismatch", "snapshot_mismatch"})

    def test_duplicate_or_unknown_runs_rejected(self):
        manifest = {"samples": [self.record("a", "benign")]}
        for rows in ([self.row("a", "benign")] * 2, [self.row("x", "benign")]):
            with self.assertRaises(ValueError):
                score(manifest, self.result(rows))

    def test_review_requires_actual_record_and_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "samples" / "SIM001"
            folder.mkdir(parents=True)
            (folder / "server.py").write_text("# inert test data\n", encoding="utf-8")
            record = {"sample_id": "SIM001", "source_directory": "samples", "snapshot_sha256": "current"}
            review = {"status": "reviewed", "snapshot_sha256": "current", "reviewer": "test reviewer",
                      "reviewed_at": "2026-11-11T09:00:00+07:00", "rubric_id": "test", "rationale": "test reasoning",
                      "label": "benign", "assessed_scope": "source_intent",
                      "evidence_refs": [{"path": "samples/SIM001/server.py", "line": 1}]}
            self.assertEqual(validate_review(review, record, root), [])
            for field, value, error in [("snapshot_sha256", "old", "STALE_REVIEW_SNAPSHOT"),
                                        ("reviewer", None, "MISSING_REVIEWER"),
                                        ("assessed_scope", "runtime_effect", "RUNTIME_EVIDENCE_REQUIRED")]:
                changed = copy.deepcopy(review)
                changed[field] = value
                self.assertIn(error, validate_review(changed, record, root))
            review["evidence_refs"][0]["path"] = "../outside.py"
            self.assertIn("INVALID_EVIDENCE_PATH", validate_review(review, record, root))

    def test_shared_methods_join_different_business_families(self):
        records = [
            {"sample_id": "SIM001", "pair_id": "SIM001", "family_id": "M01", "core_method_fingerprints": {"hook": "same"}, "content_fingerprint": None},
            {"sample_id": "SIM006", "pair_id": "SIM006", "family_id": "M02", "core_method_fingerprints": {"hook": "same"}, "content_fingerprint": None},
            {"sample_id": "BEN001", "pair_id": "SIM001", "family_id": "M01", "core_method_fingerprints": {}, "content_fingerprint": None},
        ]
        self.assertEqual(len(assign_groups(records)), 1)


if __name__ == "__main__":
    unittest.main()
