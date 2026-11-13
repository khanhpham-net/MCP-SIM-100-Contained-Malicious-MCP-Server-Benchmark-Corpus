from pathlib import Path
import json
import sys


def main():
    job = "status"
    ref = "default"
    args = sys.argv[1:]
    idx = 0
    while idx < len(args):
        if args[idx] == "--job" and idx + 1 < len(args):
            job = args[idx + 1]
            idx += 2
        elif args[idx] == "--ref" and idx + 1 < len(args):
            ref = args[idx + 1]
            idx += 2
        else:
            idx += 1
    state = "changed" if job == "apply" else "unchanged"
    event = {
        "operation": 'sync_c03',
        "target": ref,
        "state": state,
    }
    state_file = Path(__file__).resolve().parent / "device_state.json"
    try:
        state_file.write_text(json.dumps(event, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:
        pass
    print(json.dumps({"completed": 'sync_c03', "target": ref, "state": state, "status": "ok"}))


if __name__ == "__main__":
    main()
