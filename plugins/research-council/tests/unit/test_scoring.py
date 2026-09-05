import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research_graph.scoring import score_source, corroboration_summary


class ScoringTests(unittest.TestCase):
    def test_source_score_bounds(self):
        score = score_source(
            {
                "source_type": "peer-reviewed",
                "publication_date": "2026-01-01",
                "independence_group": "independent",
                "methodology": "randomized",
            }
        )
        self.assertGreaterEqual(score, 80)
        self.assertLessEqual(score, 100)

    def test_corroboration_summary(self):
        run = {
            "evidence": [
                {"evidence_id": "e1"},
                {"evidence_id": "e2"},
                {"evidence_id": "e3"},
            ],
            "claims": [
                {
                    "claim_id": "c1",
                    "supporting_evidence_ids": ["e1", "e2"],
                    "contradicting_evidence_ids": ["e3"],
                },
                {"claim_id": "c2", "supporting_evidence_ids": ["e3"], "contradicting_evidence_ids": []},
            ],
            "reviews": [
                {"claim_id": "c1", "disposition": "Approved"},
                {"claim_id": "c2", "disposition": "Contested"},
            ],
        }
        summary = corroboration_summary(run)
        self.assertIn("high_confidence", summary)
        self.assertIn("medium_confidence", summary)
        self.assertIn("low_confidence", summary)
