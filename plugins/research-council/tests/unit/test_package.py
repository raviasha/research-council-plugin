from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class PackageTests(unittest.TestCase):
    def test_repository_marketplace_has_a_unique_install_name(self):
        marketplace = ROOT.parent.parent / ".agents" / "plugins" / "marketplace.json"

        import json

        marketplace_payload = json.loads(marketplace.read_text(encoding="utf-8"))
        self.assertEqual(marketplace_payload["name"], "research-council")
        self.assertEqual(marketplace_payload["interface"]["displayName"], "Research Council")

    def test_manifest_and_marketplace_identify_the_same_plugin(self):
        manifest = ROOT / ".codex-plugin" / "plugin.json"
        marketplace = ROOT.parent.parent / ".agents" / "plugins" / "marketplace.json"
        self.assertTrue(manifest.exists(), "plugin manifest should exist")
        self.assertTrue(marketplace.exists(), "marketplace file should exist")

        import json

        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        marketplace_payload = json.loads(marketplace.read_text(encoding="utf-8"))
        entry = None
        for candidate in marketplace_payload.get("plugins", []):
            if candidate.get("name") == manifest_payload["name"]:
                entry = candidate
                break

        self.assertIsNotNone(entry, "plugin should be listed in marketplace")
        self.assertEqual(manifest_payload["name"], "research-council")
        self.assertEqual(entry.get("source", {}).get("source"), "local")
        self.assertEqual(entry.get("source", {}).get("path"), "./plugins/research-council")
        self.assertEqual(manifest_payload["skills"], "./skills/")
