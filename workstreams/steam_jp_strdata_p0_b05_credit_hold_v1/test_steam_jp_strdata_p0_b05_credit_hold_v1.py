from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("credit_hold", ROOT / "build_steam_jp_strdata_p0_b05_credit_hold_v1.py")
assert SPEC and SPEC.loader
hold = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hold)


class CreditHoldTests(unittest.TestCase):
    def test_p0_b05_contract_has_six_coordinates(self) -> None:
        coordinates, hashes = hold.contract_entries()
        self.assertEqual(len(coordinates), 6)
        self.assertEqual(len(hashes), 6)
        self.assertEqual(hold.canonical_hash(coordinates), hold.EXPECTED_COORDINATE_SHA256)

    def test_public_hold_is_source_free_and_complete(self) -> None:
        document = hold.load_hold(hold.DEFAULT_HOLD)
        self.assertEqual(len(document["entries"]), 6)
        self.assertEqual(document["distribution_policy"], {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        })
        self.assertTrue(all("ko" not in entry for entry in document["entries"]))

    def test_tmp_gate_rejects_game_root(self) -> None:
        with self.assertRaises(hold.CreditHoldError):
            hold.require_output(hold.GAME_ROOT / "MSG" / "JP", hold.TMP_ROOT)


if __name__ == "__main__":
    unittest.main()
