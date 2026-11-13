"""Read-only source inspection. Never imports or executes corpus modules."""
from pathlib import Path
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import inspect
import json
import re

from fixture_templates import C_HELPERS, M_HELPERS, S_HELPERS

ROOT = Path(__file__).resolve().parent
CORE_METHODS = (set(M_HELPERS.values()) | set(C_HELPERS.values())
                | {method for pair in S_HELPERS.values() for method in pair})

PROBE_ARTIFACTS = {
    "tool_description": {"server.py", "tools.json"},
    "input_schema_description": {"models.py", "tools.json"},
    "resource_body": {"content.txt"},
    "tool_result": {"content.txt"},
    "prompt_message": {"content.txt"},
}

TRACKED_CALLS = {
    "subprocess.run", "subprocess.Popen", "subprocess.check_output",
    "asyncio.create_subprocess_exec",
    "os.getenv", "os.environ.get",
    "HTTPConnection", "connection.request", "connection.getresponse", "conn.request", "conn.getresponse",
    "urllib.request.urlopen", "urllib.request.Request",
    "socket.create_connection",
} | {f"self.{method}" for method in CORE_METHODS} | {method for method in CORE_METHODS}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_files(folder):
    return sorted(p for p in folder.rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts and p.suffix != ".pyc")


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): digest(p.read_bytes()) for p in source_files(folder)}


def call_name(node):
    return ast.unparse(node.func)


def is_tool(function):
    return any(
        (isinstance(d, ast.Call) and ast.unparse(d.func) == "mcp.tool")
        or (isinstance(d, ast.Attribute) and ast.unparse(d) == "mcp.tool")
        for d in function.decorator_list
    )


def inspect_sample(root, sample, directory):
    sid = sample["sample_id"]
    if not re.fullmatch(r"SIM\d{3}", sid):
        raise ValueError(f"Unexpected sample ID: {sid}")
    folder = (root / directory / sid).resolve()
    if folder.parent != (root / directory).resolve():
        raise ValueError("Sample path outside corpus")
    hashes = snapshot(folder)
    issues, facts, methods, exported = [], [], {}, {}
    manifest_files = set()
    for name, artifact in sample["artifacts"].items():
        path = (root / artifact["path"]).resolve()
        if not path.is_relative_to(folder):
            raise ValueError("Artifact escapes sample directory")
        relative = path.relative_to(folder).as_posix()
        manifest_files.add(relative)
        if hashes.get(relative) != artifact["sha256"]:
            issues.append({"code": "ARTIFACT_HASH_MISMATCH", "path": artifact["path"]})
    for relative in sorted(set(hashes) - manifest_files):
        issues.append({"code": "UNMANIFESTED_FILE", "path": f"{directory}/{sid}/{relative}"})
    python_count = 0
    for path in source_files(folder):
        if path.suffix != ".py":
            continue
        python_count += 1
        relative = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_bytes())
        except (SyntaxError, ValueError) as error:
            issues.append({"code": "SYNTAX_ERROR", "path": relative, "line": getattr(error, "lineno", None)})
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in CORE_METHODS:
                    methods[node.name] = digest(ast.dump(node, include_attributes=False).encode())
                if is_tool(node):
                    if node.name in exported:
                        issues.append({"code": "DUPLICATE_TOOL_NAME", "name": node.name})
                    exported[node.name] = inspect.cleandoc(ast.get_docstring(node, clean=False) or "")
            if isinstance(node, ast.Call) and call_name(node) in TRACKED_CALLS:
                fact = {"path": relative, "line": node.lineno, "end_line": node.end_lineno,
                        "source_sha256": hashes[path.relative_to(folder).as_posix()],
                        "call": call_name(node), "positional_argument_count": len(node.args)}
                if fact["call"].startswith("subprocess.") or fact["call"] == "asyncio.create_subprocess_exec":
                    for keyword in node.keywords:
                        if keyword.arg in ("shell", "check", "timeout") and isinstance(keyword.value, ast.Constant):
                            fact[keyword.arg] = keyword.value.value
                if fact["call"] in ("os.getenv", "os.environ.get") and node.args and isinstance(node.args[0], ast.Constant):
                    fact["environment_variable_name"] = node.args[0].value
                facts.append(fact)
    tools_path = folder / "tools.json"
    try:
        tools = json.loads(tools_path.read_bytes())["tools"]
        listed = {t["name"]: inspect.cleandoc(t.get("description", "")) for t in tools}
        if len(listed) != len(tools) or exported != listed:
            issues.append({"code": "TOOL_NAME_OR_DESCRIPTION_MISMATCH"})
    except (ValueError, KeyError, OSError, TypeError):
        issues.append({"code": "INVALID_TOOLS_JSON"})
    skill = sample.get("skill_view")
    if skill:
        view = (root / skill["path"]).resolve()
        if not view.is_relative_to((root / "skill-views").resolve()):
            raise ValueError("Skill view escapes corpus")
        for name, expected in skill["sha256"].items():
            file = (view / name).resolve()
            if not file.is_relative_to(view):
                raise ValueError("Skill artifact escapes view")
            if not file.exists() or digest(file.read_bytes()) != expected:
                issues.append({"code": "SKILL_HASH_MISMATCH", "file": name})
        for name, expected in hashes.items():
            file = view / name
            if not file.exists() or digest(file.read_bytes()) != expected:
                issues.append({"code": "SKILL_SOURCE_MISMATCH", "file": name})
    content = folder / "content.txt"
    return {"sample_id": sid, "family_id": sample["family_id"],
            "pair_id": sid, "source_directory": directory,
            "snapshot_sha256": digest(canonical(hashes)), "artifacts": hashes,
            "python_files_parsed": python_count, "static_facts": facts, "issues": issues,
            "core_method_fingerprints": methods,
            "content_fingerprint": digest(content.read_bytes()) if content.exists() else None,
            "metadata_check": "static_tool_names_and_descriptions_only",
            "runtime_execution": "NOT_PERFORMED"}


def assign_groups(records):
    """Join declared families, shared behavior methods and identical text."""
    parents = {r["sample_id"]: r["sample_id"] for r in records}
    def find(item):
        while parents[item] != item:
            parents[item] = parents[parents[item]]
            item = parents[item]
        return item
    tokens = {}
    for record in records:
        sid = record["sample_id"]
        keys = ["family:" + record["family_id"]]
        if sid.startswith("SIM"):
            keys += ["method:" + name + ":" + value for name, value in record["core_method_fingerprints"].items()]
            if record["content_fingerprint"]:
                keys.append("content:" + record["content_fingerprint"])
        for key in keys:
            if key in tokens:
                parents[find(sid)] = find(tokens[key])
            else:
                tokens[key] = sid
    components = defaultdict(list)
    for sid in parents:
        components[find(sid)].append(sid)
    result = []
    for index, members in enumerate(sorted(components.values(), key=lambda x: min(x)), 1):
        name = f"GROUP{index:02d}"
        for record in records:
            if record["sample_id"] in members:
                record["recommended_split_group"] = name
        result.append({"group_id": name, "members": sorted(members), "count": len(members)})
    return result


def check_probe_surfaces(root, records):
    cases = {case["sample_id"]: case for case in json.loads((root / "scenarios.json").read_bytes())}
    seen = set()
    for record in records:
        sid = record["sample_id"]
        if not sid.startswith("SIM"):
            continue
        case = cases[sid]
        if not case["probe_surface"]:
            continue
        probe = case["probe"].encode("utf-8")
        fingerprint = digest(probe)
        if fingerprint in seen:
            record["issues"].append({"code": "DUPLICATE_PROBE_TEXT"})
        seen.add(fingerprint)
        folder = root / "samples" / sid
        probe_variants = {probe, probe.replace(b"\n", b"\\n")}
        found = {name for name in record["artifacts"] if any(v in (folder / name).read_bytes() for v in probe_variants)}

        if case["probe_surface"] == "input_schema_description":
            schema_file = (
                "models.py" if "models.py" in record["artifacts"] and any(v in (folder / "models.py").read_bytes() for v in probe_variants)
                else "service.py" if "service.py" in record["artifacts"] and any(v in (folder / "service.py").read_bytes() for v in probe_variants)
                else "core/handler.py" if "core/handler.py" in record["artifacts"] and any(v in (folder / "core" / "handler.py").read_bytes() for v in probe_variants)
                else "server.py"
            )
            expected = {schema_file, "tools.json"}
        else:
            expected = PROBE_ARTIFACTS[case["probe_surface"]]

        if found != expected or (("content.txt" in record["artifacts"]) != ("content.txt" in expected)):
            record["issues"].append({"code": "PROBE_SURFACE_CONTAMINATION", "expected": sorted(expected), "found": sorted(found)})
        if case["probe_surface"] in ("tool_description", "input_schema_description"):
            if not any(v in (root / "skill-views" / sid / "SKILL.md").read_bytes() for v in probe_variants):
                record["issues"].append({"code": "MISSING_SKILL_PROBE_SURFACE"})
        elif case["probe_surface"] in ("resource_body", "tool_result", "prompt_message"):
            py_files = [f for f in record["artifacts"] if f.endswith(".py")]
            has_content_ref = any(b"content.txt" in (folder / f).read_bytes() for f in py_files)
            if not has_content_ref:
                record["issues"].append({"code": "MISSING_CONTENT_TXT_REFERENCE"})
    return len(seen)


def run(root=ROOT):
    records, imports = [], {}
    directory, name = "samples", "manifest.json"
    raw = (root / name).read_bytes()
    imports[name] = digest(raw)
    for sample in json.loads(raw)["samples"]:
        records.append(inspect_sample(root, sample, directory))
    if len({r["sample_id"] for r in records}) != len(records):
        raise ValueError("Duplicate sample IDs")
    probe_count = check_probe_surfaces(root, records)
    groups = assign_groups(records)
    for record in records:
        write_json(root / "evaluation" / "static-evidence" / (record["sample_id"] + ".json"), record)
    reports = {}
    ver_path = root / "verification.json"
    if ver_path.exists():
        data = json.loads(ver_path.read_bytes())
        reports["verification.json"] = {
            "file_sha256": digest(ver_path.read_bytes()),
            "manifest_hash_matches": data.get("manifest_sha256") == imports[name],
            "reported_stdio_sessions": data.get("stdio_sessions_verified"),
            "provenance": "existing_report_not_rerun",
            "new_behavior_success": "NOT_ESTABLISHED_BY_THIS_STATIC_AUDIT",
        }
    report = {
        "schema_version": "1.0",
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit_script_sha256": digest(Path(__file__).read_bytes()),
        "source_manifests": imports,
        "sample_count": len(records),
        "python_files_parsed": sum(r["python_files_parsed"] for r in records),
        "issue_count": sum(len(r["issues"]) for r in records),
        "recommended_split_groups": groups,
        "unique_probe_texts": probe_count,
        "existing_runtime_reports": reports,
        "samples": records,
        "executed_samples": 0,
    }
    write_json(root / "evaluation" / "static-audit.json", report)
    print(f"Static audit: {len(records)} samples, {report['python_files_parsed']} Python files, {report['issue_count']} issues, {len(groups)} split groups; executed samples: 0")
    return report


if __name__ == "__main__":
    run()
