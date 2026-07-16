from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p0_b03", ROOT / "build_steam_jp_strdata_p0_b03_v1.py")
assert SPEC and SPEC.loader
batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch)


class SteamJpStrdataP0B03Tests(unittest.TestCase):
    def setUp(self) -> None:
        batch.configure_engine()
        batch.engine.derive_overlay = batch.derive_overlay

    def test_coordinate_contract_is_exact_p0_b03(self) -> None:
        coordinates, source_hashes, bundle = batch.engine.load_coordinate_contract()
        self.assertEqual(bundle["bundle_id"], batch.BUNDLE_ID)
        self.assertEqual(len(coordinates), 350)
        self.assertEqual(batch.engine.canonical_hash(coordinates), batch.EXPECTED_COORDINATE_SHA256)
        self.assertEqual(len(source_hashes), 350)

    def test_three_safe_format_repairs_are_scoped_to_b03(self) -> None:
        coordinates, _, _ = batch.engine.load_coordinate_contract()
        coordinate_set = {(item["block_id"], item["slot_id"]) for item in coordinates}
        self.assertEqual(set(batch.SAFE_KO_OVERRIDES), {(0, 22292), (0, 22302), (0, 22373)})
        self.assertTrue(set(batch.SAFE_KO_OVERRIDES).issubset(coordinate_set))
        self.assertTrue(all(not batch.engine.KANA_OR_CJK.search(value) for value in batch.SAFE_KO_OVERRIDES.values()))

    def test_overlay_is_source_free_and_complete(self) -> None:
        overlay, blob = batch.engine.load_overlay(batch.DEFAULT_OVERLAY)
        self.assertEqual(overlay["entry_count"], 350)
        self.assertNotIn('"source_jp_text"', blob.decode("utf-8"))
        self.assertEqual(overlay["distribution_policy"], {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        })

    def test_candidate_gate_rejects_game_root_and_other_batches(self) -> None:
        with self.assertRaises(batch.engine.StrdataP0Error):
            batch.engine.require_tmp_output(batch.engine.GAME_ROOT / "MSG" / "JP")
        with self.assertRaises(batch.engine.StrdataP0Error):
            batch.engine.require_tmp_output(
                batch.engine.REPOSITORY / "tmp" / "steam_jp_strdata_p0_b02_v1" / "candidate"
            )


if __name__ == "__main__":
    unittest.main()
