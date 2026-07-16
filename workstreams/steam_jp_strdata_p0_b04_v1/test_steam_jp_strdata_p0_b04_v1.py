from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p0_b04", ROOT / "build_steam_jp_strdata_p0_b04_v1.py")
assert SPEC and SPEC.loader
batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch)


class SteamJpStrdataP0B04Tests(unittest.TestCase):
    def setUp(self) -> None:
        batch.configure_engine()
        batch.engine.derive_overlay = batch.derive_overlay

    def test_coordinate_contract_is_exact_p0_b04(self) -> None:
        coordinates, source_hashes, bundle = batch.engine.load_coordinate_contract()
        self.assertEqual(bundle["bundle_id"], batch.BUNDLE_ID)
        self.assertEqual(len(coordinates), 350)
        self.assertEqual(batch.engine.canonical_hash(coordinates), batch.EXPECTED_COORDINATE_SHA256)
        self.assertEqual(len(source_hashes), 350)

    def test_repair_scope_and_nonhangul_allowlist_are_small(self) -> None:
        coordinates, _, _ = batch.engine.load_coordinate_contract()
        coordinate_set = {(item["block_id"], item["slot_id"]) for item in coordinates}
        expected = batch.BULLET_REPAIRS | set(batch.SAFE_KO_OVERRIDES)
        self.assertEqual(len(expected), 16)
        self.assertTrue(expected.issubset(coordinate_set))
        self.assertEqual(batch.ALLOWED_NON_HANGUL, {(1, 876), (1, 1608)})

    def test_overlay_is_source_free_and_has_no_japanese_glyphs(self) -> None:
        overlay, blob = batch.engine.load_overlay(batch.DEFAULT_OVERLAY)
        self.assertEqual(overlay["entry_count"], 350)
        self.assertNotIn('"source_jp_text"', blob.decode("utf-8"))
        for entry in overlay["entries"]:
            key = (entry["block_id"], entry["slot_id"])
            self.assertIsNone(batch.engine.KANA_OR_CJK.search(entry["ko"]))
            if not batch.REAL_HANGUL.search(entry["ko"]):
                self.assertIn(key, batch.ALLOWED_NON_HANGUL)

    def test_candidate_gate_rejects_game_root_and_other_batches(self) -> None:
        with self.assertRaises(batch.engine.StrdataP0Error):
            batch.engine.require_tmp_output(batch.engine.GAME_ROOT / "MSG" / "JP")
        with self.assertRaises(batch.engine.StrdataP0Error):
            batch.engine.require_tmp_output(
                batch.engine.REPOSITORY / "tmp" / "steam_jp_strdata_p0_b03_v1" / "candidate"
            )


if __name__ == "__main__":
    unittest.main()
