import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research_graph.report import write_package


class ReportTests(unittest.TestCase):
    def test_report_writes_expected_artifacts(self):
        with (ROOT / "tests" / "fixtures" / "valid_run" / "run.json").open("r", encoding="utf-8") as handle:
            run = json.load(handle)

        with tempfile.TemporaryDirectory(prefix="rc-report-") as tmp:
            output = write_package(run, tmp)
            self.assertNotIn("error", output)
            self.assertTrue(Path(output["docx"]).exists())
            self.assertTrue(Path(output["evidence_json"]).exists())
            self.assertTrue(Path(output["audit_json"]).exists())
