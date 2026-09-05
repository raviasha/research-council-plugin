"""CLI entrypoint for run validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research_graph import validate_run
from scripts.research_graph.models import load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Research Council run output.")
    parser.add_argument("--run", required=True, help="Path to run.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_path = Path(args.run)
    run_payload = load_json(run_path)
    issues = validate_run(run_payload)
    payload = {
        "valid": len(issues) == 0,
        "issue_count": len(issues),
        "issues": [issue.as_dict() for issue in issues],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
