import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research_graph.models import Disposition, canonical_json


class ModelTests(unittest.TestCase):
    def test_dispositions_match_spec(self):
        self.assertEqual(
            [item.value for item in Disposition],
            [
                "Approved",
                "Approved-with-caveat",
                "Contested",
                "Insufficient-evidence",
                "Rejected",
            ],
        )

    def test_canonical_json_sorts_keys(self):
        payload = {"b": 1, "a": {"z": 2, "y": 1}}
        self.assertEqual(canonical_json(payload), '{"a":{"y":1,"z":2},"b":1}')
