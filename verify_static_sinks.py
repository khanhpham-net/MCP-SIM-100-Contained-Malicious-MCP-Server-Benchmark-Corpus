"""Verify static sinks, dual-mode worker contracts, and Group P surface integrity."""
from pathlib import Path
import ast
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

FORBIDDEN_TOKENS = [
    "create_subprocess_shell",
    "os.popen",
    "base64",
    "8710",
    '".env"',
    "'.env'",
    "api_key",
    "secret_key",
    "bot_token",
    "access_key",
    "auth_context",
    '"token"',
]

C_WORKERS = {
    "C01": ("counter_sync.py", "SIM026"),
    "C02": ("indicator_service.py", "SIM031"),
    "C03": ("device_dispatcher.py", "SIM036"),
    "C04": ("asset_subsystem.py", "SIM041"),
    "C05": ("task_executor.py", "SIM046"),
}


def check_ast_parse():
    py_files = sorted(list(ROOT.glob("samples/**/*.py")) + list(ROOT.glob("skill-views/**/*.py")))
    if not py_files:
        raise RuntimeError("No Python files found in samples/ or skill-views/")
    for path in py_files:
        try:
            ast.parse(path.read_bytes(), filename=str(path))
        except SyntaxError as e:
            raise RuntimeError(f"Syntax error in {path}: {e}")
    print(f"[CHECK 1 PASSED] AST parsed {len(py_files)} Python files successfully.")


def check_group_c_gradient():
    for i in range(26, 51):
        sid = f"SIM{i:03d}"
        edge = ((i - 1) % 5) + 1
        sample_dir = ROOT / "samples" / sid

        py_files = list(sample_dir.glob("**/*.py"))

        if edge in (1, 2):
            target_file = sample_dir / ("server.py" if edge == 1 else "service.py")
            content = target_file.read_text(encoding="utf-8")
            if "shell=True" not in content:
                raise RuntimeError(f"{sid} (E{edge}) missing shell=True in {target_file.name}")
            if "--job" not in content or "apply" not in content or "--ref" not in content:
                raise RuntimeError(f"{sid} (E{edge}) missing --job/apply/--ref arguments")
        else:
            # E3, E4, E5 must have zero shell keyword arguments in all python files
            for pf in py_files:
                tree = ast.parse(pf.read_bytes())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        for kw in node.keywords:
                            if kw.arg == "shell":
                                raise RuntimeError(f"{sid} (E{edge}) has forbidden 'shell' keyword in {pf}")

            if edge == 3:
                handler = sample_dir / "core" / "handler.py"
                txt = handler.read_text(encoding="utf-8")
                if "create_subprocess_exec" not in txt or "--job" not in txt or "apply" not in txt or "--ref" not in txt:
                    raise RuntimeError(f"{sid} E3 missing create_subprocess_exec with --job apply --ref")
            elif edge == 4:
                domain = sample_dir / "domain.py"
                txt = domain.read_text(encoding="utf-8")
                if "subprocess.run" not in txt or "--job" not in txt or "apply" not in txt or "--ref" not in txt:
                    raise RuntimeError(f"{sid} E4 missing subprocess.run with --job apply --ref")
            elif edge == 5:
                domain = sample_dir / "domain.py"
                txt = domain.read_text(encoding="utf-8")
                if "subprocess.Popen" not in txt or "--job" not in txt or "apply" not in txt or "--ref" not in txt:
                    raise RuntimeError(f"{sid} E5 missing subprocess.Popen with --job apply --ref")

    print("[CHECK 2 PASSED] Group C shell vs. argv gradient verified across SIM026-SIM050.")


def check_forbidden_tokens():
    targets = sorted(list(ROOT.glob("samples/**/*")) + list(ROOT.glob("skill-views/**/*")))
    files = [p for p in targets if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"]

    violations = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                violations.append((str(f.relative_to(ROOT)), token))

    if violations:
        msg = "\n".join(f"  {path}: contains forbidden token {tok!r}" for path, tok in violations[:20])
        raise RuntimeError(f"Forbidden tokens found ({len(violations)} occurrences):\n{msg}")

    print(f"[CHECK 3 PASSED] Zero forbidden tokens across {len(files)} corpus files.")


def check_worker_scripts():
    results = {}
    for code, (worker_name, sid) in C_WORKERS.items():
        worker_path = ROOT / "samples" / sid / worker_name
        if not worker_path.exists():
            raise RuntimeError(f"Worker script {worker_path} not found")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            tmp_worker = tmp_path / worker_name
            tmp_worker.write_bytes(worker_path.read_bytes())
            state_file = tmp_path / "device_state.json"

            # 1. Run with --job apply --ref ROW1
            cmd_apply = [sys.executable, "-I", "-B", str(tmp_worker), "--job", "apply", "--ref", "ROW1"]
            proc1 = subprocess.run(cmd_apply, cwd=tmp_dir, capture_output=True, text=True, check=True)
            out1 = json.loads(proc1.stdout.strip())
            if not state_file.exists():
                raise RuntimeError(f"Worker {worker_name} did not create device_state.json on apply")
            state1 = json.loads(state_file.read_text(encoding="utf-8").strip())

            if state1.get("state") != "changed" or state1.get("target") != "ROW1":
                raise RuntimeError(f"Worker {worker_name} apply state invalid: {state1}")
            if out1.get("state") != "changed" or out1.get("target") != "ROW1":
                raise RuntimeError(f"Worker {worker_name} apply output invalid: {out1}")

            # 2. Run with --job status --ref ROW1
            cmd_status = [sys.executable, "-I", "-B", str(tmp_worker), "--job", "status", "--ref", "ROW1"]
            proc2 = subprocess.run(cmd_status, cwd=tmp_dir, capture_output=True, text=True, check=True)
            out2 = json.loads(proc2.stdout.strip())
            state2 = json.loads(state_file.read_text(encoding="utf-8").strip())

            if state2.get("state") != "unchanged" or state2.get("target") != "ROW1":
                raise RuntimeError(f"Worker {worker_name} status state invalid: {state2}")
            if out2.get("state") != "unchanged" or out2.get("target") != "ROW1":
                raise RuntimeError(f"Worker {worker_name} status output invalid: {out2}")

            results[worker_name] = {
                "sample_id": sid,
                "family": code,
                "apply_result": {"stdout": out1, "device_state": state1},
                "status_result": {"stdout": out2, "device_state": state2},
                "verified": True,
            }

    evidence_dir = ROOT / "evaluation" / "runtime-evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "workers.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"[CHECK 4 PASSED] Verified 5 worker scripts in tempdir; saved to evaluation/runtime-evidence/workers.json.")


def check_group_p_surfaces():
    scenarios_path = ROOT / "scenarios.json"
    manifest_path = ROOT / "manifest.json"
    if not scenarios_path.exists() or not manifest_path.exists():
        raise RuntimeError("scenarios.json or manifest.json not found")
    scenarios = {s["sample_id"]: s for s in json.loads(scenarios_path.read_bytes())}
    manifest = {s["sample_id"]: s for s in json.loads(manifest_path.read_bytes())["samples"]}

    for i in range(76, 101):
        sid = f"SIM{i:03d}"
        case = scenarios[sid]
        code = manifest[sid]["family_id"]
        probe = case["probe"]

        # P03 reads content.txt into preview
        if code == "P03":
            sample_dir = ROOT / "samples" / sid
            py_files = [f for f in sample_dir.glob("**/*.py") if f.name != "__init__.py"]
            reads_content = False
            for pf in py_files:
                txt = pf.read_text(encoding="utf-8")
                if "content.txt" in txt and '"preview": note' in txt:
                    reads_content = True
                    break
            if not reads_content:
                raise RuntimeError(f"{sid} (P03) does not read content.txt into preview")

        # Check SKILL.md probe inclusion/exclusion
        skill_path = ROOT / "skill-views" / sid / "SKILL.md"
        if not skill_path.exists():
            raise RuntimeError(f"Missing {skill_path}")
        skill_text = skill_path.read_text(encoding="utf-8")

        if code in ("P02", "P03", "P05"):
            if probe in skill_text:
                raise RuntimeError(f"{sid} ({code}) leaked probe into SKILL.md")
        elif code in ("P01", "P04"):
            if probe not in skill_text:
                raise RuntimeError(f"{sid} ({code}) missing probe in SKILL.md")

    print("[CHECK 5 PASSED] Group P surfaces verified across SIM076-SIM100.")


def check_production_depth():
    min_lines = float("inf")
    max_lines = 0
    total_lines = 0

    for i in range(1, 101):
        sid = f"SIM{i:03d}"
        sample_dir = ROOT / "samples" / sid
        py_files = [f for f in sample_dir.glob("**/*.py") if f.name != "__init__.py"]

        sample_line_count = sum(len(f.read_text(encoding="utf-8").splitlines()) for f in sample_dir.glob("**/*.py"))
        if sample_line_count < 75:
            raise RuntimeError(f"{sid} has only {sample_line_count} Python lines (< 75 required)")

        min_lines = min(min_lines, sample_line_count)
        max_lines = max(max_lines, sample_line_count)
        total_lines += sample_line_count

        catalog_found = False
        for pf in py_files:
            txt = pf.read_text(encoding="utf-8")
            if "_CATALOG_DATA" in txt:
                tree = ast.parse(txt)
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "_CATALOG_DATA":
                                if isinstance(node.value, ast.List) and len(node.value.elts) >= 4:
                                    catalog_found = True
                                    break
            if catalog_found:
                break
        if not catalog_found:
            raise RuntimeError(f"{sid} missing _CATALOG_DATA with >= 4 records")

    avg_lines = total_lines / 100.0
    print(f"[CHECK 6 PASSED] Production depth verified: min={min_lines}, avg={avg_lines:.1f}, max={max_lines} lines/sample (all >= 75 lines, all have _CATALOG_DATA >= 4 records).")


def main():
    check_ast_parse()
    check_group_c_gradient()
    check_forbidden_tokens()
    check_worker_scripts()
    check_group_p_surfaces()
    check_production_depth()
    print("STATIC_SINK_OK")


if __name__ == "__main__":
    main()
