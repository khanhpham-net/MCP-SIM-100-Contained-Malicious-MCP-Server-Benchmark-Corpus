"""Resolve one portable fixture config on Duy's machine; does not launch it."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parent


def prepare(sample_id, executable):
    manifest = json.loads((ROOT / "manifest.json").read_bytes())
    sample = next((s for s in manifest["samples"] if s["sample_id"] == sample_id), None)
    if sample is None:
        raise ValueError(f"Unknown sample ID: {sample_id}")
    folder = ROOT / "samples" / sample_id
    config = json.loads((folder / "mcp.json").read_bytes())
    entry = next(iter(config["mcpServers"].values()))
    entry["command"] = str(Path(executable).resolve())
    if not Path(entry["command"]).is_file():
        raise ValueError("Python executable does not exist")
    extra_args = entry.get("args", [])[2:]
    entry["args"] = ["-B", str((folder / "server.py").resolve()), *extra_args]
    target = ROOT / "launch" / (sample_id + ".json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    print(prepare(args.sample, args.python))
