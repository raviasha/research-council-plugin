import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research_graph.validate import validate_run


def load_fixture(name: str) -> dict:
    path = ROOT / "tests" / "fixtures" / name / "run.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class ValidateTests(unittest.TestCase):
    def issue_codes(self, run: dict) -> set[str]:
        return {item.code for item in validate_run(run)}

    def test_missing_locator(self):
        run = load_fixture("missing_locator")
        self.assertIn("FR06_MISSING_LOCATOR", self.issue_codes(run))

    def test_missing_high_importance_challenge(self):
        run = load_fixture("missing_challenge")
        self.assertIn("FR07_MISSING_CHALLENGE", self.issue_codes(run))

    def test_invalid_disposition(self):
        run = load_fixture("invalid_disposition")
        self.assertIn("FR12_INVALID_DISPOSITION", self.issue_codes(run))
