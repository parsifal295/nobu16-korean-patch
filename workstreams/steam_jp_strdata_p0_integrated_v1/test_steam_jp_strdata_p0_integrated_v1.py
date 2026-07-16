from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p0_integrated", ROOT / "build_steam_jp_strdata_p0_integrated_v1.py")
assert SPEC and SPEC.loader
integration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integration)


class P0IntegratedTests(unittest.TestCase):
    def test_components_are_pinned_nonoverlapping_and_complete(self) -> None:
        translated, deferred, metadata = integration.load_components()
        keys = {(entry["block_id"], entry["slot_id"]) for entry in translated + deferred}
        self.assertEqual(len(translated), 1400)
        self.assertEqual(len(deferred), 6)
        self.assertEqual(len(keys), 1406)
        self.assertEqual(len(metadata), 5)

    def test_combined_overlay_is_source_free(self) -> None:
        document, blob = integration.load_combined(integration.COMBINED_PATH)
        self.assertEqual(document["translated_entry_count"], 1400)
        self.assertEqual(document["deferred_credit_entry_count"], 6)
        self.assertNotIn('"source_jp_text"', blob.decode("utf-8"))
        self.assertEqual(document["distribution_policy"], {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        })

    def test_tmp_gate_rejects_game_root(self) -> None:
        with self.assertRaises(integration.IntegrationError):
            integration.require_tmp(integration.GAME_ROOT / "MSG" / "JP")


if __name__ == "__main__":
    unittest.main()
