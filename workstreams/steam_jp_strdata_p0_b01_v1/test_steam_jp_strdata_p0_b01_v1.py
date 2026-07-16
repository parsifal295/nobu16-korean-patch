from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p0_builder", ROOT / "build_steam_jp_strdata_p0_b01_v1.py")
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class SteamJpStrdataP0Tests(unittest.TestCase):
    def test_coordinate_contract_is_exact_p0_bundle(self) -> None:
        coordinates, source_hashes, bundle = builder.load_coordinate_contract()
        self.assertEqual(bundle["bundle_id"], builder.BUNDLE_ID)
        self.assertEqual(len(coordinates), 350)
        self.assertEqual(builder.canonical_hash(coordinates), builder.EXPECTED_COORDINATE_SHA256)
        self.assertEqual(len(source_hashes), 350)

    def test_default_overlay_is_source_free_and_complete(self) -> None:
        overlay, blob = builder.load_overlay(builder.DEFAULT_OVERLAY)
        self.assertEqual(overlay["entry_count"], 350)
        self.assertEqual(overlay["distribution_policy"], {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        })
        self.assertNotIn('"source_jp_text"', blob.decode("utf-8"))
        self.assertTrue(all("source_jp" not in entry or len(entry["source_jp_utf16le_sha256"]) == 64 for entry in overlay["entries"]))

    def test_candidate_path_gate_rejects_game_root(self) -> None:
        with self.assertRaises(builder.StrdataP0Error):
            builder.require_tmp_output(builder.GAME_ROOT / "MSG" / "JP")

    def test_candidate_path_gate_allows_owned_tmp(self) -> None:
        builder.require_tmp_output(builder.SAFE_TMP_ROOT / "test" / "candidate")


if __name__ == "__main__":
    unittest.main()
