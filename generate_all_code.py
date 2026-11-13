"""Generate all_code.txt (optimized for AI review, <300KB) and all_code_full.txt (complete dump)."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

CORE_SCRIPTS = [
    "build.py",
    "fixture_templates.py",
    "catalog.py",
    "audit_corpus.py",
    "verify_static_sinks.py",
    "prepare_evaluation.py",
    "create_handoff.py",
    "score_results.py",
    "test_evaluation.py",
    "prepare_config.py",
]

CORE_DOCS = [
    "README.md",
    "SCANNER_HANDOFF.md",
    "EVALUATION_GUIDE.md",
    "SAMPLE_INDEX.md",
]

# Representative sample IDs covering all 4 groups (M, C, S, P) and all 5 edges (E1-E5)
REP_SAMPLE_IDS = [
    # Group M (E1 to E5)
    "SIM001", "SIM002", "SIM003", "SIM004", "SIM005",
    # Group C (E1 to E5)
    "SIM026", "SIM027", "SIM028", "SIM029", "SIM030",
    # Group S (E1 to E5)
    "SIM051", "SIM052", "SIM053", "SIM054", "SIM055",
    # Group P (E1 to E5)
    "SIM076", "SIM077", "SIM078", "SIM079", "SIM080",
]


def write_export_file(output_path, file_list, header_note):
    count = 0
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"MCP-SIM-100 BENCHMARK SOURCE CODE\n")
        out.write(f"Root: {ROOT}\n")
        out.write(f"Summary: {header_note}\n")
        out.write("=" * 90 + "\n\n")

        for rel_path in file_list:
            p = ROOT / rel_path
            if not p.is_file():
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"[Error reading file: {e}]"

            out.write("=" * 90 + "\n")
            out.write(f"FILE: {rel_path}\n")
            out.write("=" * 90 + "\n\n")
            out.write(content)
            out.write("\n\n")
            count += 1
    print(f"Wrote {count} files to {output_path} ({output_path.stat().st_size:,} bytes)")


def main():
    # 1. Prepare file list for all_code.txt (Optimized)
    opt_files = []
    # Add core scripts
    for s in CORE_SCRIPTS:
        if (ROOT / s).exists():
            opt_files.append(s)
    # Add core docs
    for d in CORE_DOCS:
        if (ROOT / d).exists():
            opt_files.append(d)

    # Add representative samples
    for sid in REP_SAMPLE_IDS:
        sample_dir = ROOT / "samples" / sid
        if sample_dir.exists():
            for f in sorted(sample_dir.rglob("*")):
                if f.is_file():
                    opt_files.append(str(f.relative_to(ROOT)).replace("\\", "/"))
        skill_dir = ROOT / "skill-views" / sid
        if skill_dir.exists():
            for f in sorted(skill_dir.rglob("*")):
                if f.is_file() and f.suffix in (".md", ".py", ".json", ".toml"):
                    opt_files.append(str(f.relative_to(ROOT)).replace("\\", "/"))
        static_ev = ROOT / "evaluation" / "static-evidence" / f"{sid}.json"
        if static_ev.exists():
            opt_files.append(str(static_ev.relative_to(ROOT)).replace("\\", "/"))

    # Write all_code.txt
    write_export_file(
        ROOT / "all_code.txt",
        opt_files,
        f"Exported {len(opt_files)} priority files (Core Scripts + Docs + 20 Representative Samples for E1-E5 across M, C, S, P). Fits within AI chat context without truncation."
    )

    # 2. Prepare file list for all_code_full.txt (Full dump)
    full_files = []
    # Scripts and Docs first
    for s in CORE_SCRIPTS:
        if (ROOT / s).exists():
            full_files.append(s)
    for d in CORE_DOCS:
        if (ROOT / d).exists():
            full_files.append(d)

    # All files in samples, skill-views, evaluation
    for folder in ["samples", "skill-views", "evaluation"]:
        f_dir = ROOT / folder
        if f_dir.exists():
            for f in sorted(f_dir.rglob("*")):
                if f.is_file() and not f.name.endswith(".zip"):
                    rel = str(f.relative_to(ROOT)).replace("\\", "/")
                    if rel not in full_files:
                        full_files.append(rel)

    # Root json files
    for rj in ["manifest.json", "benchmark-manifest.json", "scan-results-template.json"]:
        if (ROOT / rj).exists():
            full_files.append(rj)

    write_export_file(
        ROOT / "all_code_full.txt",
        full_files,
        f"Full raw dump of all {len(full_files)} files in MCP-SIM-100."
    )


if __name__ == "__main__":
    main()
